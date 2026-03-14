from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.db.models import ProtectedError
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .base_view import AppLoginRequiredMixin


class CrudMetadataMixin:
    model_label = ''
    model_label_plural = ''
    page_badge = ''
    page_description = ''
    create_url_name = ''
    update_url_name = ''
    delete_url_name = ''
    list_url_name = ''
    status_url_name = ''
    submit_label = '保存する'
    delete_message = '削除しました。'
    create_message = '登録しました。'
    update_message = '更新しました。'
    protected_error_message = '関連データがあるため削除できません。'
    table_fields = ()
    template_name = ''
    status_field = ''

    def get_status_choices(self):
        if not self.status_field:
            return []

        model_field = self.model._meta.get_field(self.status_field)
        if not getattr(model_field, 'choices', None):
            return []
        return list(model_field.choices)

    def get_default_status_value(self):
        status_choices = self.get_status_choices()
        if not status_choices:
            return None

        for status_value, _ in status_choices:
            if self.model._default_manager.filter(**{self.status_field: status_value}).exists():
                return status_value
        return status_choices[0][0]

    def get_current_status_value(self):
        return getattr(self, 'current_status_value', None)

    def get_list_url(self):
        if self.status_field and self.status_url_name:
            status_value = None
            if hasattr(self, 'object') and self.object is not None:
                status_value = getattr(self.object, self.status_field, None)
            if not status_value:
                status_value = self.get_current_status_value() or self.get_default_status_value()
            if status_value:
                return reverse(self.status_url_name, args=[status_value])
        return reverse(self.list_url_name)

    def get_create_url(self):
        return reverse(self.create_url_name)

    def get_update_url(self, obj):
        return reverse(self.update_url_name, args=[obj.pk])

    def get_delete_url(self, obj):
        return reverse(self.delete_url_name, args=[obj.pk])

    def get_status_url(self, status_value):
        if self.status_field and self.status_url_name:
            return reverse(self.status_url_name, args=[status_value])
        return self.get_list_url()


class CrudValueFormatterMixin:
    @staticmethod
    def format_value(value):
        if value in (None, ''):
            return '-'
        if isinstance(value, bool):
            return 'はい' if value else 'いいえ'
        if isinstance(value, Decimal):
            return format(value, 'f')
        return str(value)


class BaseRecordListView(AppLoginRequiredMixin, CrudMetadataMixin, CrudValueFormatterMixin, ListView):
    context_object_name = 'objects'
    template_name = 'billing/crud/object_list.html'
    current_status_value = None

    def get_queryset(self):
        queryset = super().get_queryset()
        status_choices = dict(self.get_status_choices())
        if not status_choices:
            self.current_status_value = None
            return queryset

        status_value = self.kwargs.get('status') or self.get_default_status_value()
        if status_value not in status_choices:
            raise Http404('指定されたステータスは存在しません。')

        self.current_status_value = status_value
        return queryset.filter(**{self.status_field: status_value})

    def get_table_headers(self):
        return [label for _, label in self.table_fields]

    def get_cell_value(self, obj, field_name):
        display_method = getattr(obj, f'get_{field_name}_display', None)
        if callable(display_method):
            return self.format_value(display_method())
        return self.format_value(getattr(obj, field_name))

    def build_table_rows(self, objects):
        rows = []
        for obj in objects:
            rows.append(
                {
                    'object': obj,
                    'display_name': str(obj),
                    'cells': [self.get_cell_value(obj, field_name) for field_name, _ in self.table_fields],
                    'update_url': self.get_update_url(obj),
                    'delete_url': self.get_delete_url(obj),
                }
            )
        return rows

    def get_status_navigation(self):
        status_choices = self.get_status_choices()
        if not status_choices:
            return []

        return [
            {
                'value': status_value,
                'label': status_label,
                'count': self.model._default_manager.filter(**{self.status_field: status_value}).count(),
                'url': self.get_status_url(status_value),
                'is_active': status_value == self.get_current_status_value(),
            }
            for status_value, status_label in status_choices
        ]

    def get_current_status_label(self):
        status_map = dict(self.get_status_choices())
        return status_map.get(self.get_current_status_value(), '')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_status_label = self.get_current_status_label()
        context.update(
            {
                'page_title': f'{self.model_label_plural}一覧',
                'page_heading': self.model_label_plural,
                'page_badge': self.page_badge,
                'page_description': self.page_description,
                'create_url': self.get_create_url(),
                'create_label': f'{self.model_label}を登録',
                'table_headers': self.get_table_headers(),
                'table_rows': self.build_table_rows(self.object_list),
                'status_navigation': self.get_status_navigation(),
                'current_status_label': current_status_label,
                'empty_message': (
                    f'{current_status_label}の{self.model_label_plural}はまだ登録されていません。'
                    if current_status_label
                    else f'{self.model_label_plural}はまだ登録されていません。'
                ),
                'dashboard_url': reverse('billing:dashboard'),
            }
        )
        return context


class BaseRecordCreateView(AppLoginRequiredMixin, CrudMetadataMixin, CreateView):
    template_name = 'billing/crud/object_form.html'

    def get_success_url(self):
        return self.get_list_url()

    def form_valid(self, form):
        messages.success(self.request, f'{self.model_label}を{self.create_message}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': f'{self.model_label}登録',
                'page_heading': f'{self.model_label}登録',
                'page_badge': self.page_badge,
                'page_description': self.page_description,
                'submit_label': self.submit_label,
                'cancel_url': self.get_list_url(),
            }
        )
        return context


class BaseRecordUpdateView(AppLoginRequiredMixin, CrudMetadataMixin, UpdateView):
    template_name = 'billing/crud/object_form.html'
    submit_label = '更新する'

    def get_success_url(self):
        return self.get_list_url()

    def form_valid(self, form):
        messages.success(self.request, f'{self.model_label}を{self.update_message}')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': f'{self.model_label}編集',
                'page_heading': f'{self.model_label}編集',
                'page_badge': self.page_badge,
                'page_description': self.page_description,
                'submit_label': self.submit_label,
                'cancel_url': self.get_list_url(),
            }
        )
        return context


class BaseRecordDeleteView(AppLoginRequiredMixin, CrudMetadataMixin, DeleteView):
    template_name = 'billing/crud/object_confirm_delete.html'

    def get_success_url(self):
        return self.get_list_url()

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, f'{self.model_label}を{self.delete_message}')
            return response
        except ProtectedError:
            messages.error(self.request, f'{self.model_label}は{self.protected_error_message}')
            return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'page_title': f'{self.model_label}削除',
                'page_heading': f'{self.model_label}削除',
                'page_badge': self.page_badge,
                'page_description': self.page_description,
                'cancel_url': self.get_list_url(),
            }
        )
        return context


class BaseRecordWithItemFormSetMixin(CrudMetadataMixin):
    item_formset_class = None
    item_formset_prefix = 'items'
    item_formset_title = ''
    item_formset_description = ''
    item_formset_limit = None
    item_visibility_suffix = 'VISIBLE'
    success_message = ''

    def initialize_object(self):
        self.object = self.get_object() if self.kwargs.get('pk') is not None else None

    def get_item_formset(self):
        kwargs = {
            'instance': self.object or self.model(),
            'prefix': self.item_formset_prefix,
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs['data'] = self.prepare_item_formset_data(self.request.POST.copy())
        item_formset = self.item_formset_class(**kwargs)
        return self.configure_item_formset(item_formset)

    def get_item_visibility_key(self, item_form):
        return f'{item_form.prefix}-{self.item_visibility_suffix}'

    def get_item_visibility_value(self, item_form):
        return self.request.POST.get(self.get_item_visibility_key(item_form))

    def prepare_item_formset_data(self, data):
        total_forms = int(data.get(f'{self.item_formset_prefix}-TOTAL_FORMS', 0) or 0)
        hidden_values = {'0', 'false', 'False', 'off'}

        for index in range(total_forms):
            row_prefix = f'{self.item_formset_prefix}-{index}'
            visibility = data.get(f'{row_prefix}-{self.item_visibility_suffix}')
            delete_value = data.get(f'{row_prefix}-DELETE')
            instance_id = data.get(f'{row_prefix}-id')

            if visibility not in hidden_values:
                continue
            if delete_value in {'on', 'true', 'True', '1'}:
                continue
            if instance_id not in (None, ''):
                continue

            data[f'{row_prefix}-display_order'] = str(index + 1)
            if f'{row_prefix}-quantity' in data:
                data[f'{row_prefix}-quantity'] = '1.00'

            for field_name in ('description', 'unit_label', 'unit_price', 'notes', 'quote_item'):
                field_key = f'{row_prefix}-{field_name}'
                if field_key in data:
                    data[field_key] = ''

        return data

    def configure_item_formset(self, item_formset):
        has_existing_items = any(form.instance.pk for form in item_formset.forms)
        visible_count = 0

        for index, item_form in enumerate(item_formset.forms):
            item_form.visibility_key = self.get_item_visibility_key(item_form)
            item_form.is_displayed = self.is_item_form_displayed(item_form, index, has_existing_items)
            item_form.visibility_value = '1' if item_form.is_displayed else '0'
            if item_form.is_displayed:
                visible_count += 1

        if self.request.method not in ('POST', 'PUT') and visible_count == 0 and item_formset.forms:
            item_formset.forms[0].is_displayed = True
            item_formset.forms[0].visibility_value = '1'
            visible_count = 1

        item_formset.initial_visible_count = visible_count
        return item_formset

    def is_item_form_displayed(self, item_form, index, has_existing_items):
        if self.request.method in ('POST', 'PUT'):
            if self.request.POST.get(f'{item_form.prefix}-DELETE') in {'on', 'true', 'True', '1'}:
                return False
            if item_form.errors:
                return True

            posted_visibility = self.get_item_visibility_value(item_form)
            if posted_visibility in {'1', 'true', 'True', 'on'}:
                return True
            if posted_visibility in {'0', 'false', 'False', 'off'}:
                return False

            if item_form.instance.pk:
                return True
            return self.item_form_has_input(item_form)

        if item_form.instance.pk:
            return True
        return not has_existing_items and index == 0

    def item_form_has_input(self, item_form):
        ignored_fields = {'DELETE', 'display_order'}
        for field_name in item_form.fields:
            if field_name in ignored_fields:
                continue
            value = self.request.POST.get(f'{item_form.prefix}-{field_name}')
            if value not in (None, ''):
                return True
        return False

    def post(self, request, *args, **kwargs):
        self.initialize_object()
        form = self.get_form()
        item_formset = self.get_item_formset()
        if form.is_valid() and item_formset.is_valid():
            return self.forms_valid(form, item_formset)
        return self.forms_invalid(form, item_formset)

    def synchronize_item_display_order(self):
        if not hasattr(self.object, 'items'):
            return

        for index, item in enumerate(self.object.items.order_by('display_order', 'id'), start=1):
            if item.display_order != index:
                item.__class__.objects.filter(pk=item.pk).update(display_order=index)

    def forms_valid(self, form, item_formset):
        with transaction.atomic():
            self.object = form.save()
            item_formset.instance = self.object
            item_formset.save()
            self.synchronize_item_display_order()
            if hasattr(self.object, 'refresh_amounts'):
                self.object.refresh_amounts()
        messages.success(self.request, f'{self.model_label}を{self.success_message}')
        return redirect(self.get_success_url())

    def forms_invalid(self, form, item_formset):
        return self.render_to_response(self.get_context_data(form=form, item_formset=item_formset))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        item_formset = kwargs.get('item_formset') or self.get_item_formset()
        context.update(
            {
                'item_formset': item_formset,
                'item_formset_title': self.item_formset_title,
                'item_formset_description': self.item_formset_description,
                'item_formset_limit': self.item_formset_limit,
                'item_formset_initial_visible_count': getattr(item_formset, 'initial_visible_count', 0),
            }
        )
        return context


class BaseRecordCreateWithItemFormSetView(BaseRecordWithItemFormSetMixin, BaseRecordCreateView):
    success_message = '登録しました。'


class BaseRecordUpdateWithItemFormSetView(BaseRecordWithItemFormSetMixin, BaseRecordUpdateView):
    success_message = '更新しました。'
