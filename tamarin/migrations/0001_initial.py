# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'S3LoggedBucket'
        db.create_table('tamarin_s3loggedbucket', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
            ('log_bucket_name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('monitor_bucket', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('tamarin', ['S3LoggedBucket'])

        # Adding model 'S3LogRecord'
        db.create_table('tamarin_s3logrecord', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('bucket_owner', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('bucket', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['tamarin.S3LoggedBucket'])),
            ('request_dtime', self.gf('django.db.models.fields.DateTimeField')()),
            ('remote_ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
            ('requester', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('request_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('operation', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('key', self.gf('django.db.models.fields.TextField')()),
            ('request_uri', self.gf('django.db.models.fields.TextField')()),
            ('http_status', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('error_code', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('bytes_sent', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('object_size', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('total_time', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('turnaround_time', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
            ('referrer', self.gf('django.db.models.fields.TextField')()),
            ('user_agent', self.gf('django.db.models.fields.TextField')()),
            ('version_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('tamarin', ['S3LogRecord'])


    def backwards(self, orm):
        
        # Deleting model 'S3LoggedBucket'
        db.delete_table('tamarin_s3loggedbucket')

        # Deleting model 'S3LogRecord'
        db.delete_table('tamarin_s3logrecord')


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
            'http_status': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.TextField', [], {}),
            'object_size': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'operation': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'referrer': ('django.db.models.fields.TextField', [], {}),
            'remote_ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'request_dtime': ('django.db.models.fields.DateTimeField', [], {}),
            'request_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'request_uri': ('django.db.models.fields.TextField', [], {}),
            'requester': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'total_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'turnaround_time': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            'user_agent': ('django.db.models.fields.TextField', [], {}),
            'version_id': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        }
    }

    complete_apps = ['tamarin']
