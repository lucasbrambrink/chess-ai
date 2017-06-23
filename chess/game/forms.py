from django import forms
from .models import Piece


class InitGameForm(forms.Form):
    color = forms.BooleanField(label='Color')


class CommandForm(forms.Form):
    command = forms.CharField(max_length=255)
    player_key = forms.HiddenInput()

    def set_label(self, color):
        """choose opposite as last color"""
        label = '%s to Move ' % ('White' if color == Piece.BLACK else 'Black')
        self.fields['command'].label = label
