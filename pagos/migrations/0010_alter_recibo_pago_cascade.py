"""Alter Recibo.pago to CASCADE and non-nullable."""

from django.db import migrations, models
import django.db.models.deletion


def delete_orphan_recibos(apps, schema_editor):
    Recibo = apps.get_model('pagos', 'Recibo')
    Recibo.objects.filter(pago__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0009_alter_recibo_pago_set_null'),
    ]

    operations = [
        migrations.RunPython(delete_orphan_recibos, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name='recibo',
            name='pago',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='recibo', to='pagos.pago'),
        ),
    ]
