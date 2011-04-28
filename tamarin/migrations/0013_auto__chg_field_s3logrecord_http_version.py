# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'S3LogRecord.http_version'
        db.alter_column('tamarin_s3logrecord', 'http_version', self.gf('django.db.models.fields.CharField')(max_length=15, null=True))


    def backwards(self, orm):
        
        # User chose to not deal with backwards NULL issues for 'S3LogRecord.http_version'
        raise RuntimeError("Cannot reverse this migration. 'S3LogRecord.http_version' and its values cannot be restored.")


    models = {
        'tamarin.s3loggedbucket': {
            'Meta': {'object_name': 'S3LoggedBucket'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'log_bucket_name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'monitor_bucket': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'})
        },
        'tamarin.s3logrecord': {
            'Meta': {'object_name': 'S3LogRecord'},
            'bucket': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['tamarin.S3LoggedBucket']"}),
            'bucket_owner': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'bytes_sent': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'http_status': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'http_version': ('django.db.models.fields.CharField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {}),
            'object_size': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'referrer': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'remote_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'request_dtime': ('django.db.models.fields.DateTimeField', [], {}),
            'request_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'request_method': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'request_uri': ('django.db.models.fields.TextField', [], {}),
            'requester': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'total_time': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'turnaround_time': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_agent': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'version_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['tamarin']
