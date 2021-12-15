# forms.py
from django import forms


class CardForm(forms.Form):
    CHOICE_LIST = [('UR', 'UR'), ('SR', 'SR'), ('R', 'R'), ('N', 'N'),]
    rarity = forms.ChoiceField(choices=CHOICE_LIST)
    copies = forms.IntegerField()
    extra = forms.BooleanField(required=False)


class BoxForm(forms.Form):
    CHOICE_LIST = [
        (80, 80),
        (100, 100),
        (180, 180),
        (200, 200),
    ]
    packs_in_box = forms.ChoiceField(choices=CHOICE_LIST)

CardFormSet = forms.formset_factory(CardForm, extra=1)