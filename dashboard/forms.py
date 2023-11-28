from django import forms
from .models import GolfCourse, Tee, Team, Player, Game, Hole, TeeTime
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit


class GolfCourseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new course",
                "name",
                "initials",
                "hole_count",
                "tee_time_link",
                "website_link",
                "city",
                "state",
                "zip_code",
                "card",
                "overview",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = GolfCourse
        fields = [
            "name",
            "initials",
            "hole_count",
            "tee_time_link",
            "website_link",
            "city",
            "state",
            "zip_code",
            "card",
            "overview",
        ]


class EditGolfCourseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Edit course",
                "name",
                "initials",
                "hole_count",
                "tee_time_link",
                "website_link",
                "city",
                "state",
                "zip_code",
                "card",
                "overview",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = GolfCourse
        fields = [
            "name",
            "initials",
            "hole_count",
            "tee_time_link",
            "website_link",
            "city",
            "state",
            "zip_code",
            "card",
            "overview",
        ]


class TeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new tee",
                "color",
                "distance",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Tee
        fields = ["color", "distance"]


class TeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new Team",
                "game",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Team
        fields = ["game"]


class PlayerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new Player",
                "name",
                "handicap",
                "photo",
                "user_account",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Player
        exclude = ["added_by"]


class GameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new Game",
                "game_type",
                "course",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Game
        fields = ["game_type", "course"]


class HoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new Hole",
                "name",
                "nickname",
                "par",
                "course",
                "order",
                "handicap",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Hole
        fields = [
            "name",
            "nickname",
            "par",
            "course",
            "order",
            "handicap",
        ]


class EditHoleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Edit Hole",
                "nickname",
                "par",
                "handicap",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Hole
        fields = [
            "nickname",
            "par",
            "handicap",
        ]


class TeeTimeForm(forms.ModelForm):
    tee_time = forms.DateTimeField(input_formats=["%m-%d-%Y %H:%M"])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new Tee Time",
                "course",
                "tee_time",
                "players",
                "holes_to_play",
                "which_holes",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = TeeTime
        fields = ["course", "tee_time", "players", "holes_to_play", "which_holes"]
