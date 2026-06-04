"""Generated migration to allow NULL on Recibo.pago and use SET_NULL on delete."""

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pagos', '0008_alter_pago_monto_alter_pago_reserva_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recibo',
            name='pago',
            field=models.OneToOneField(null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='recibo', to='pagos.pago'),
        ),
    ]
