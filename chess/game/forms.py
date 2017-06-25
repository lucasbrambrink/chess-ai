from django import forms
from .models import Piece


class InitGameForm(forms.Form):
    COLORS = (
        (Piece.WHITE, 'White'),
        (Piece.BLACK, 'Black')
    )
    color = forms.ChoiceField(choices=COLORS)


class CommandForm(forms.Form):
    command = forms.CharField(max_length=255, label_suffix='')
    player_key = forms.HiddenInput()


    def set_label(self, color):
        """choose opposite as last color"""
        label = '%s to move ' % ('White' if color == Piece.BLACK else 'Black')
        self.fields['command'].label = label


class ChatForm(forms.Form):
    chat_line = forms.Textarea()
    player_key = forms.HiddenInput()

    class Meta:
        fields = ('chat_line', 'player_key')
