from django.contrib import admin

from tamarin.models import S3LoggedBucket, S3LogRecord

class S3LoggedBucketAdmin(admin.ModelAdmin):
    """
    Admin configuration for S3LoggedBucket model.
    """
    list_display = ['name', 'log_bucket_name', 'monitor_bucket']
    list_filter = ['monitor_bucket']
    search_fields = ['name', 'log_bucket_name']
    ordering = ['name']
admin.site.register(S3LoggedBucket, S3LoggedBucketAdmin)
