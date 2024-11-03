from django.core.exceptions import ValidationError


def validate_comma_separated_address(value):
    address_sections = value.split(',')
    if len(address_sections) != 3:
        raise ValidationError('Address format should be "<Street>, <Postal_Code City>, <Country>"')

    if len(address_sections[1].split(' ')) == 2:
        raise ValidationError('Postal code and city should not be empty')