from django import forms
from .models import Piece


class CommandForm(forms.Form):
    command = forms.CharField(max_length=255)

    def set_label(self, color):
        """choose opposite as last color"""
        label = '%s to Move: ' % ('White' if color == Piece.BLACK else 'Black')
        self.fields['command'].label = label
