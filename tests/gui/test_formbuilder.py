import yaml

from sleap.gui.dialogs import formbuilder
import math


def test_formbuilder_dialog(qtbot):
    dialog = formbuilder.FormBuilderModalDialog(form_name="labeled_clip_form")

    dialog.set_message("foo")
    assert dialog.message_fields[0].text() == "foo"

    dialog.set_message("bar")
    assert dialog.message_fields[0].text() == "bar"


def test_formbuilder(qtbot):
    form_yaml = """
- name: method
  label: Method
  type: stacked
  default: two
  options: one,two,three,four

  one:
    - name: per_video
      label: Samples Per Video
      type: int
      default: 20
      range: 1,3000
    - name: sampling_method
      label: Sampling method
      type: list
      options: random,stride
      default: stride

  two:
    - name: node
      label: Node
      type: list
    - name: foo
      label: Avogadro
      type: sci
      default: 6.022e23

  three:
    - name: node
      label: Node
      type: list

  four:
    - name: lossWeight
      label: Loss Weight
      type: double
      default: 1.0

"""

    items_to_create = yaml.load(form_yaml, Loader=yaml.SafeLoader)

    field_options_lists = dict(node=("first option", "second option"))

    layout = formbuilder.FormBuilderLayout(
        items_to_create, field_options_lists=field_options_lists
    )

    form_data = layout.get_form_data()

    assert "node" in form_data
    assert form_data["node"] == "first option"

    layout.set_field_options("node", ("new option", "another new option"))

    form_data = layout.get_form_data()
    assert form_data["node"] == "new option"


def test_optional_spin_widget(qtbot):
    widget = formbuilder.OptionalSpinWidget()

    widget.setValue(3)
    assert widget.value() == 3

    widget.check_widget.setChecked(True)
    assert widget.value() is None

    widget.check_widget.setChecked(False)
    assert widget.value() == 3

    widget.setValue("none")
    assert widget.value() is None


def test_auto_double_widget(qtbot):
    widget = formbuilder.OptionalSpinWidget(type="double", none_string="auto")

    widget.setValue(3.2)
    assert widget.value() == 3.2

    widget.check_widget.setChecked(True)
    assert widget.value() is "auto"

    widget.check_widget.setChecked(False)
    assert widget.value() == 3.2

    widget.setValue("auto")
    assert widget.value() == "auto"

    widget.setValue(3.2)
    assert widget.value() == 3.2

    widget.setValue(None)
    assert widget.value() == "auto"


def test_text_or_list_widget(qtbot):
    widget = formbuilder.TextOrListWidget()

    widget.setValue("foo")
    assert widget.value() == "foo"
    assert widget.mode == "text"

    widget.set_options(["a", "b", "c"])
    assert widget.mode == "list"

    widget.setValue("b")
    assert widget.value() == "b"

    widget.setMode("text")
    assert widget.value() == "b"


def test_string_list_widget(qtbot):
    widget = formbuilder.StringListWidget()

    widget.setValue("foo bar")
    x = widget.getValue()
    print(x)
    assert x == ["foo", "bar"]

    widget.setValue(["zip", "cab"])
    assert widget.text() == "zip cab"


def test_exponential_spin_box(qtbot):
    """Test ExponentialSpinBox setValue and stepBy methods."""
    widget = formbuilder.ExponentialSpinBox()
    qtbot.addWidget(widget)

    widget.setValue(1.0)
    assert math.isclose(widget.value(), 1.0, rel_tol=1e-3)

    # Test that stepping by positive numbers multiplies value by 10
    widget.stepBy(1)
    assert math.isclose(widget.value(), 10.0, rel_tol=1e-3)

    widget.stepBy(1)
    assert math.isclose(widget.value(), 100.0, rel_tol=1e-3)

    # Test that stepping by negative numbers multiplies value by 0.1
    widget.stepBy(-1)
    assert math.isclose(widget.value(), 10.0, rel_tol=1e-3)

    widget.stepBy(-1)
    assert math.isclose(widget.value(), 1.0, rel_tol=1e-3)

    # Test numbers other than 1 and -1
    widget.stepBy(2)
    assert math.isclose(widget.value(), 100.0, rel_tol=1e-3)

    widget.stepBy(-2)
    assert math.isclose(widget.value(), 1.0, rel_tol=1e-3)


def test_formbuilder_lossweight(qtbot):
    form_yaml = """
- name: lossWeight
  label: Loss Weight
  type: double
  default: 1.0
"""

    items_to_create = yaml.load(form_yaml, Loader=yaml.SafeLoader)
    layout = formbuilder.FormBuilderLayout(items_to_create)

    form_data = layout.get_form_data()
    print(form_data)

    # form_data = [{lossWeight : 1}]
    assert "lossWeight" in form_data
    assert form_data["lossWeight"] == 1.0

    # Make sure the field is exponentialSpinbox
    loss_weight_field = layout.fields["lossWeight"]
    assert isinstance(loss_weight_field, formbuilder.ExponentialSpinBox)

    loss_weight_field.stepBy(1)
    assert loss_weight_field.value() == 10.0

    loss_weight_field.stepBy(1)
    assert loss_weight_field.value() == 100.0

    loss_weight_field.stepBy(1)
    assert loss_weight_field.value() == 1000.0

    loss_weight_field.stepBy(1)
    assert loss_weight_field.value() == 1000.0

    loss_weight_field.stepBy(-1)
    assert loss_weight_field.value() == 100.0

    loss_weight_field.stepBy(-1)
    assert loss_weight_field.value() == 10.0

    loss_weight_field.stepBy(-1)
    assert loss_weight_field.value() == 1.0

    loss_weight_field.stepBy(-1)
    assert loss_weight_field.value() == 0.10

    loss_weight_field.stepBy(-1)
    assert loss_weight_field.value() == 0.01

    loss_weight_field.stepBy(-1)
    assert loss_weight_field.value() == 0.0

    # Test numbers other than 1 and -1
    loss_weight_field.stepBy(3)
    assert loss_weight_field.value() == 1.0
