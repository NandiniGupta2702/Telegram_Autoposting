# Generated by Django 4.2.16 on 2024-09-23 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0027_minid_destination_channel'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChannelMinId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_channel', models.CharField(max_length=255)),
                ('destination_channel', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=15)),
                ('min_id', models.BigIntegerField(default=0)),
            ],
            options={
                'unique_together': {('source_channel', 'destination_channel', 'phone_number')},
            },
        ),
    ]
