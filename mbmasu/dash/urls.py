from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views
from . import responsible, statist

urlpatterns = [
    path('', views.dash_index, name='dash_index'),
    path('logout', views.dash_logout, name='dash_logout'),
    path('add_xlsx_file', views.dash_add_xlsx_file, name='dash_add_xlsx_file'),
    path('users_list', views.users_list, name='users_list'),
    path('users_list/<int:user_id>', views.user, name='user'),
    path('companies_list', views.companies_list, name='companies_list'),
    path('companies_list/<int:company_id>', views.company, name='company'),
    path('download_file/<str:path>', views.download_file, name='download_file'),
    path('save_user', views.save_user, name='save_user'),
    path('save_company', views.save_company, name='save_company'),
    path('save_company_changes', views.save_company_changes, name='save_company_changes'),
    path('get_menu_content', views.get_menu_content, name='get_menu_content'),
    path('appoint_responsible_for_order', views.appoint_responsible_for_order, name='appoint_responsible_for_order'),
    path('appoint_responsible_for_order_list', views.appoint_responsible_for_order_list, name='appoint_responsible_for_order_list'),
    path('new_orders_ready_to_proceed_list', responsible.new_orders_ready_to_proceed_list, name='new_orders_ready_to_proceed_list'),
    path('new_orders_ready_to_proceed_list/<int:order_id>', responsible.order_ready_to_proceed,
         name='order_ready_to_proceed'),
    path('appoint_expert_for_order_after_temp_stop_check_list', views.appoint_expert_for_order_after_temp_stop_check_list,
         name='appoint_expert_for_order_after_temp_stop_check_list'),
    path('save_ready_for_ok_orders', views.save_ready_for_ok_orders, name='save_ready_for_ok_orders'),
    path('save_orders_for_protocol', views.save_orders_for_protocol, name='save_orders_for_protocol'),
    path('all_orders_list', views.all_orders_list, name='all_orders_list'),
    path('all_orders_list/<int:order_id>', views.order_info, name='order_info'),

    path('get_user_role_name', views.get_user_role_name, name='get_user_role_name'),
    path('appoint_expert_for_order_check_list', views.appoint_expert_for_order_check_list,
         name='appoint_expert_for_order_check_list'),
    path('delete_preliminary_check_from_distribution', responsible.delete_preliminary_check_from_distribution, name='delete_preliminary_check_from_distribution'),
    path('delete_after_temp_stop_check_from_distribution', responsible.delete_after_temp_stop_check_from_distribution, name='delete_after_temp_stop_check_from_distribution'),

    path('remade_order_send_to_subcotractor_date_list', views.remade_order_send_to_subcotractor_date_list,
         name='remade_order_send_to_subcotractor_date_list'),
    path('remade_order_send_to_subcotractor_date_list/<int:order_id>',
         views.remade_order_send_to_subcotractor_date,
         name='remade_order_send_to_subcotractor_date'),
    path('save_remade_order_send_to_subcotractor_date', views.save_remade_order_send_to_subcotractor_date, name='save_remade_order_send_to_subcotractor_date'),

    path('appoint_expert_for_order_check', views.appoint_expert_for_order_check,
         name='appoint_expert_for_order_check'),
    path('appoint_expert_for_order_after_temp_stop_check', views.appoint_expert_for_order_after_temp_stop_check,
         name='appoint_expert_for_order_after_temp_stop_check'),

    path('orders_new_send_for_check_preliminary_list', responsible.orders_new_send_for_check_preliminary_list, name='orders_new_send_for_check_preliminary_list'),
    path('orders_new_send_for_check_preliminary_list/<int:order_id>', responsible.orders_new_send_for_check_preliminary,
         name='orders_new_send_for_check_preliminary'),
    path('save_order_new_send_for_check_preliminary', responsible.save_order_new_send_for_check_preliminary, name='save_order_new_send_for_check_preliminary'),
    path('orders_new_for_expert_to_check_after_temp_stop_list', responsible.orders_new_for_expert_to_check_after_temp_stop_list,
         name='orders_new_for_expert_to_check_after_temp_stop_list'),
    path('orders_new_for_expert_to_check_after_temp_stop_list/<int:order_id>', responsible.orders_new_for_expert_to_check_after_temp_stop,
         name='orders_new_for_expert_to_check_after_temp_stop'),
    path('save_checked_docs_after_temp_stop', responsible.save_checked_docs_after_temp_stop,
         name='save_checked_docs_after_temp_stop'),

    path('check_if_user_appointed_for_order', responsible.check_if_user_appointed_for_order,
         name='check_if_user_appointed_for_order'),
    path('get_categories_list', responsible.get_categories_list, name='get_categories_list'),
    path('save_data_preliminary_check', responsible.save_data_preliminary_check, name='save_data_preliminary_check'),
    path('orders_temp_stop_date_list', responsible.orders_temp_stop_date_list, name='orders_temp_stop_date_list'),
    path('orders_temp_stop_date_list/<int:order_id>', responsible.order_temp_stop_date, name='orders_temp_stop_date'),
    path('save_temp_stop_date', responsible.save_temp_stop_date, name='save_temp_stop_date'),
    path('orders_temp_stop_without_notification_list', responsible.orders_temp_stop_without_notification_list, name='orders_temp_stop_without_notification_list'),
    path('orders_temp_stop_without_notification_list/<int:order_id>', responsible.order_without_notification, name='order_without_notification'),
    path('save_pez_notification', responsible.save_pez_notification, name='save_pez_notification'),
    path('orders_temp_stop_with_notification_before_remade_date_list', responsible.orders_temp_stop_with_notification_before_remade_date_list, name='orders_temp_stop_with_notification_before_remade_date_list'),
    path('orders_temp_stop_remadeorder_date_list', responsible.orders_temp_stop_remadeorder_date_list, name='orders_temp_stop_remadeorder_date_list'),
    path('orders_temp_stop_remadeorder_date_list/<int:order_id>', responsible.order_temp_stop_remadeorder_date,
         name='order_temp_stop_remadeorder_date'),
    path('save_temp_stop_remadeorder_date', responsible.save_temp_stop_remadeorder_date, name='save_temp_stop_remadeorder_date'),
    path('orders_temp_stop_with_notification_check_list', responsible.orders_temp_stop_with_notification_check_list,
         name='orders_temp_stop_with_notification_check_list'),
    path('orders_temp_stop_with_notification_sent_for_check_list', responsible.orders_temp_stop_with_notification_sent_for_check_list,
         name='orders_temp_stop_with_notification_sent_for_check_list'),
    path('orders_temp_stop_with_notification_check_list/<int:order_id>', responsible.orders_temp_stop_with_notification_check,
         name='orders_temp_stop_with_notification_check'),
    path('save_order_send_for_check_after_temp_stop', responsible.save_order_send_for_check_after_temp_stop, name='save_order_send_for_check_after_temp_stop'),

    path('orders_temp_stop_remade_order_decision_list', responsible.orders_temp_stop_remade_order_decision_list,
         name='orders_temp_stop_remade_order_decision_list'),
    path('orders_temp_stop_remade_order_decision_list/<int:order_id>', responsible.order_temp_stop_remade_order_decision,
         name='order_temp_stop_remade_order_decision'),
    path('save_temp_stop_remade_order_decision', responsible.save_temp_stop_remade_order_decision,
         name='save_temp_stop_remade_order_decision'),
    path('orders_refuse_preliminary_list', responsible.orders_refuse_preliminary_list,
         name='orders_refuse_preliminary_list'),
    path('orders_refuse_preliminary_list/<int:order_id>', responsible.order_refuse_preliminary, name='order_refuse_preliminary'),
    path('save_order_refuse_preliminary', responsible.save_order_refuse_preliminary,
         name='save_order_refuse_preliminary'),
    path('orders_refuse_remade_order_list', responsible.orders_refuse_remade_order_list,
         name='orders_refuse_remade_order_list'),
    path('orders_refuse_remade_order_list/<int:order_id>', responsible.order_refuse_remade_order,
         name='order_refuse_remade_order'),
    path('save_remade_order_refuse', responsible.save_remade_order_refuse,
         name='save_remade_order_refuse'),
    path('orders_ez_doc_list', responsible.orders_ez_doc_list,
         name='orders_ez_doc_list'),
    path('orders_ez_doc_list/<int:order_id>', responsible.order_ez_doc,
         name='order_ez_doc'),
    path('save_ez_doc', responsible.save_ez_doc,
         name='save_ez_doc'),
    path('orders_ez_pdf_list', responsible.orders_ez_pdf_list,
         name='orders_ez_pdf_list'),
    path('orders_ez_pdf_list/<int:order_id>', responsible.order_ez_pdf,
         name='order_ez_pdf'),
    path('save_ez_pdf', responsible.save_ez_pdf,
         name='save_ez_pdf'),
    path('orders_new_for_expert_to_check_preliminary_list', responsible.orders_new_for_expert_to_check_preliminary_list,
         name='orders_new_for_expert_to_check_preliminary_list'),
    path('orders_new_for_expert_to_check_preliminary_list/<int:order_id>', responsible.order_new_for_expert_to_check_preliminary,
         name='order_new_for_expert_to_check_preliminary'),
    path('save_checked_docs_preliminary', responsible.save_checked_docs_preliminary, name='save_checked_docs_preliminary'),
    path('orders_sent_for_preliminary_check_list', responsible.orders_sent_for_preliminary_check_list,
         name='orders_sent_for_preliminary_check_list'),
    path('orders_all_callback_list', responsible.orders_all_callback_list,
         name='orders_all_callback_list'),
    path('orders_all_callback_list/<int:order_id>', responsible.order_callback,
         name='order_callback'),
    path('save_order_callback', responsible.save_order_callback,
         name='save_order_callback'),
    path('ready_for_ok_orders_list', views.ready_for_ok_orders_list,
         name='ready_for_ok_orders_list'),
    path('ready_for_ok_orders_download', views.ready_for_ok_orders_download,
         name='ready_for_ok_orders_download'),
    path('appointed_for_ok_orders_list', views.appointed_for_ok_orders_list,
         name='appointed_for_ok_orders_list'),

    ##статист
    path('statist/new_orders_preliminary_list', statist.new_orders_preliminary_list, name='statist_new_orders_preliminary_list'),
    path('statist/new_orders_preliminary_list/<int:order_id>', statist.order_preliminary_check, name='order_preliminary_check'),
    path('statist/save_data_preliminary_check_statist', statist.save_data_preliminary_check_statist,
         name='save_data_preliminary_check_statist'),
    path('statist/statist_temp_stop_orders_for_singing_list', statist.statist_temp_stop_orders_for_singing_list,
         name='statist_temp_stop_orders_for_singing_list'),
    path('statist/statist_refuse_orders_for_singing_list', statist.statist_refuse_orders_for_singing_list,
         name='statist_refuse_orders_for_singing_list'),
    path('statist/statist_temp_stop_orders_for_singing_list/<int:order_id>', statist.statist_docs_singed,
         name='temp_stop_docs_singed'),
    path('statist/save_data_documents_signed_statist', statist.save_data_documents_signed_statist,
         name='save_data_documents_signed_statist'),
    path('statist/statist_refuse_orders_not_preliminary_list', statist.statist_refuse_orders_not_preliminary_list,
         name='statist_refuse_orders_not_preliminary_list'),
    path('statist/statist_refuse_orders_not_preliminary_list/<int:order_id>', statist.statist_refuse_order_not_preliminary,
         name='statist_refuse_order_not_preliminary'),
    path('statist/save_data_refuse_order_not_preliminary_statist', statist.save_data_refuse_order_not_preliminary_statist,
         name='save_data_refuse_order_not_preliminary_statist'),
    path('statist/statist_ez_for_signing_list', statist.statist_ez_for_signing_list,
         name='statist_ez_for_signing_list'),
    path('statist/statist_ez_for_signing_list/<int:order_id>', statist.statist_ez_for_signing, name='statist_ez_for_signing'),
    path('statist/save_data_ez_for_singing_statist', statist.save_data_ez_for_singing_statist, name='save_data_ez_for_singing_statist'),
    path('statist/statist_ez_on_signing_list', statist.statist_ez_on_signing_list,
         name='statist_ez_on_signing_list'),
    path('statist/statist_ez_on_signing_list/<int:order_id>', statist.statist_ez_singed,
         name='statist_ez_singed'),

    # path('', views.signin, name='signin'),
    # url(r'^$', views.index, name='login_index'),
    # url(r'^signin', views.signin, name='signin'),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)