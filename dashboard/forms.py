from django import forms
from django_json_widget.widgets import JSONEditorWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from .models import GolfCourse, Tee, Team, Player, Game, Hole, HoleScore, TeeTime


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


class EditTeeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Edit Tee",
                "color",
                "distance",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Tee
        fields = ["color", "distance"]


class EditTeamForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Edit Team",
                "name",
                "players",
                "handicap",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Team
        exclude = ["game"]


class PlayerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Create a new Player",
                "first_name",
                "last_name",
                "phone",
                "email",
                "handicap",
                "photo",
                "user_account",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Player
        exclude = ["added_by"]


class EditPlayerForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Edit Player",
                "first_name",
                "last_name",
                "phone",
                "email",
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
                "course",
                "game_type",
                "holes_played",
                "which_holes",
                "buy_in",
                "skin_cost",
                "use_teams",
                "use_skins",
                "league_game",
                "payout_positions",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Game
        fields = [
            "course",
            "game_type",
            "holes_played",
            "which_holes",
            "buy_in",
            "skin_cost",
            "use_teams",
            "use_skins",
            "league_game",
            "payout_positions",
        ]


class EditGameForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Edit Game",
                "course",
                "date_played",
                "game_type",
                "holes_played",
                "which_holes",
                "buy_in",
                "skin_cost",
                "use_teams",
                "use_skins",
                "league_game",
                "payout_positions",
                "players",
                "status",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = Game
        fields = [
            "course",
            "date_played",
            "game_type",
            "holes_played",
            "which_holes",
            "buy_in",
            "skin_cost",
            "use_teams",
            "use_skins",
            "league_game",
            "payout_positions",
            "players",
            "status",
        ]


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


class EditHoleScoreForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Edit Hole Score",
                "strokes",
            ),
            Submit("submit", "Submit", css_class="btn btn-primary btn-sm"),
        )

    class Meta:
        model = HoleScore
        fields = ["strokes"]


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
