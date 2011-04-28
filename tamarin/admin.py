"""
ModelAdmin classes for the tamarin package.
"""
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

class S3LogRecordAdmin(admin.ModelAdmin):
    """
    Admin configuration for S3LogRecord model.
    """
    list_display = [
        'admin_bucket_name', 'key', 'remote_ip', 'http_status',
        'bytes_sent', 'object_size', 'request_dtime',
    ]
    list_filter = ['http_status']
    search_fields = ['request_ip', 'request_uri']
    ordering = ['-request_dtime']

    def admin_bucket_name(self, obj):
        """
        Returns the name of the log's monitored bucket.
        
        :param S3LogRecord obj: The object whose bucket name to retrieve.
        :rtype: str
        :returns: The name of the bucket being monitored in this log.
        """
        return obj.bucket.name

admin.site.register(S3LogRecord, S3LogRecordAdmin)
