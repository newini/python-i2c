from django.db import models

class Data(models.Model):
    """
    Data with huminity, temperature, eCO2, TVOC
    """

    # Fields
    create_at = models.DateTimeField(help_text='Created Datetime')
    huminity = models.FloatField(help_text='Huminity')
    temperature = models.FloatField(help_text='Temperature')
    eCO2 = models.IntegerField(help_text='eCO2')
    TVOC = models.IntegerField(help_text='TVOC')

    ## Metadata
    #class Meta:
    #    ordering = ['-my_field_name']

    ## Methods
    #def get_absolute_url(self):
    #    """Returns the url to access a particular instance of MyModelName."""
    #    return reverse('model-detail-view', args=[str(self.id)])

    #def __str__(self):
    #    """String for representing the MyModelName object (in Admin site etc.)."""
    #    return self.my_field_name
