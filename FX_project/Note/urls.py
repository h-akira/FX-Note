from django.urls import path
from .views import history, chart_detail ,chart_index, histories2edit, chart_add, chart_edit, chart_update, chart_delete, chart_image, none2edit, chart_image_day, diary, calendar_index, diary_create, diary_update, diary_delete, chart_image_review, review, review_later, review_index, review_update, review_create, review_delete, speed_order, market_settlement, position_update

app_name = 'Note'

urlpatterns = [
    path('history/',history, name='history'),
    path('chart/index/',chart_index, name='chart_index'),
    path('chart/generate/',histories2edit, name='chart_generate'),
    path('chart/create/',none2edit, name='chart_create'),
    path('chart/add/',chart_add, name='chart_add'),
    path('chart/edit/<int:id>',chart_edit, name='chart_edit'),
    path('chart/update/<int:id>',chart_update, name='chart_update'),
    path('chart/delete/<int:id>',chart_delete, name='chart_delete'),
    path('chart/detail/<int:id>',chart_detail, name='chart_detail'),
    path('chart/image/<int:id>',chart_image, name='chart_image'),
    path('chart/image/day/<str:pair>/<int:year>/<int:month>/<int:day>',chart_image_day, name='chart_image_day'),
    path('diary/<int:year>/<int:month>/<int:day>',diary, name='diary'),
    path('diary/<int:year>/<int:month>/<int:day>/<str:option>',diary, name='diary_option'),
    path('diary/create/<int:year>/<int:month>/<int:day>',diary_create, name='diary_create'),
    path('diary/update/<int:id>',diary_update, name='diary_update'),
    path('diary/delete/<int:id>',diary_delete, name='diary_delete'),
    path('calendar/<int:year>/<int:month>',calendar_index, name='calendar'),
    path('calendar/',calendar_index, name='calendar_now'),
    path('review/image/<int:id>',chart_image_review, name='chart_image_review'),
    path('review/',review_index, name='review_index'),
    path('review/<int:id>',review, name='review'),
    path('review/<int:id>/later/<str:delta>',review_later, name='review_later'),
    path('review/update/<int:id>',review_update, name='review_update'),
    path('review/create/',review_create, name='review_create'),
    path('review/delete/<int:id>',review_delete, name='review_delete'),
    path('review/<int:id>/position/',speed_order, name='speed_order'),  # ReviewTableのid
    path('review/position/<int:id>',market_settlement, name='market_settlement'),  # PositionTableのid
    path('review/position/<int:id>/update/',position_update, name='position_update'),  # PositionTableのid
]
