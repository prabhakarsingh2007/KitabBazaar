from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecom', '0003_coupon_address_order_orderitem_pyment_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Pyment',
            new_name='Payment',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='Pyment_id',
            new_name='Payment_id',
        ),
        migrations.RenameField(
            model_name='order',
            old_name='adderss_id',
            new_name='address_id',
        ),
    ]
