from django.urls import path

from . import views

urlpatterns = [
    #path("", views.index_page, name="index_page"), TESTING 
    path("", views.index, name="index"),
    # CUSTOME LOGOUT 
    path('accounts/logout/', views.custom_logout, name='account_logout'),
    # Record audio 
    path('upload-audio/', views.upload_audio, name='upload_audio'),
    # Transcripte-Audio url NOTE I think NOT BE ON USE
    path('transcript/<str:filename>/', views.transcript_audio_view, name='transcript_audio'),
    path('analyze-page/<str:filename>/', views.analyze_transcript_view, name='analyze_transcript_page'),
    path('analyze-result/<str:filename>/', views.analyze_transcript_process, name='analyze_transcript_result'),
    # NOTE save AI editable Analysis
    path('save-analysis/', views.save_edited_result, name='save_edited_result'),
    # NOTE save AI editable summary
    path('save-summary/', views.save_edited_summary, name='save_edited_summary'),
    # SHOW AI SUMMARY
    path('ai-summary/<str:filename>/', views.ai_summary, name='ai_summary'),
    # GENERATE PDF
    path('generate-pdf/<int:layout_id>/<str:filename>/', views.generate_pdf, name='generate_pdf'),
    
]
