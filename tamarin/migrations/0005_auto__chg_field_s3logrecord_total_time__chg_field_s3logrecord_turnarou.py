# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'S3LogRecord.total_time'
        db.alter_column('tamarin_s3logrecord', 'total_time', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'S3LogRecord.turnaround_time'
        db.alter_column('tamarin_s3logrecord', 'turnaround_time', self.gf('django.db.models.fields.PositiveIntegerField')())

        # Changing field 'S3LogRecord.http_status'
        db.alter_column('tamarin_s3logrecord', 'http_status', self.gf('django.db.models.fields.PositiveIntegerField')())


    def backwards(self, orm):
        
        # Changing field 'S3LogRecord.total_time'
        db.alter_column('tamarin_s3logrecord', 'total_time', self.gf('django.db.models.fields.PositiveSmallIntegerField')())

        # Changing field 'S3LogRecord.turnaround_time'
        db.alter_column('tamarin_s3logrecord', 'turnaround_time', self.gf('django.db.models.fields.PositiveSmallIntegerField')())

        # Changing field 'S3LogRecord.http_status'
        db.alter_column('tamarin_s3logrecord', 'http_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')())


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
            'bytes_sent': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'error_code': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'http_status': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'http_version': ('django.db.models.fields.CharField', [], {'max_length': '15'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {}),
            'object_size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'referrer': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'remote_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'request_dtime': ('django.db.models.fields.DateTimeField', [], {}),
            'request_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
            'request_method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'request_uri': ('django.db.models.fields.TextField', [], {}),
            'requester': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'total_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'turnaround_time': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'user_agent': ('django.db.models.fields.TextField', [], {}),
            'version_id': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        }
    }

    complete_apps = ['tamarin']
