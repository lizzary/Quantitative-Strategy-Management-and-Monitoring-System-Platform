import uuid
from django.core.exceptions import ValidationError
from django.db import models

#标签名字段
class LabelNameField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label name')
        super().__init__(*args, **kwargs)


#标签值字段
class LabelCharField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)

class LabelDateField(models.DateField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)

class LabelDateTimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)

class LabelFloatField(models.FloatField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)

class LabelIntegerField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)


class LabelTextField(models.TextField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)

class LabelTimeField(models.TimeField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)

class LabelUUIDField(models.UUIDField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label UID')
        kwargs.setdefault('editable', False)
        kwargs.setdefault('unique', True)
        kwargs.setdefault('default', uuid.uuid4)
        kwargs.setdefault('db_index', True)
        super().__init__(*args, **kwargs)

class LabelChoiceField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', [('timer','timer'),('counter','counter'),('read_only','read_only')])
        kwargs.setdefault('verbose_name', 'label type')
        kwargs.setdefault('help_text', 'When displayed on a webpage, if it is a timer or stepper, and the container type of the label is "interactive," the API for the label trigger will be called.')
        super().__init__(*args, **kwargs)

class LabelsContainerField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'belongs to')
        kwargs.setdefault('default', 'None')
        kwargs.setdefault('help_text', 'This value is automatically managed by the system to prevent the label from being reused across models. Please do not modify this value unless necessary.')
        super().__init__(*args, **kwargs)

class LabelDurationField(models.DurationField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', 'label value')
        super().__init__(*args, **kwargs)

class LabelDisplayFormatField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name','label display format')
        kwargs.setdefault('default','<label name>: <separator><label value>')
        kwargs.setdefault('help_text', "When displayed on a webpage, 'label name' and 'label value' will be replaced with actual values, using 'separator' to achieve grouping. The spacing between groups guided by 'separator' is determined by the system, and 'separator' can appear a maximum of two times. The default is: label name: label value.")
        super().__init__(*args, **kwargs)

    def validate(self,value, model_instance):
        super().validate(value, model_instance)

        if '<label value>' not in value:
            raise ValidationError('The expression must contain at least one "<label value>" segment.')

        if value.count('<separator>') > 2:
            raise ValidationError('The "<separator>" segment can appear a maximum of two times in the expression.')

