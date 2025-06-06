#Para definir el formulario
from django import forms

#formulario para el metodo de biseccion
class BisectionForm(forms.Form):
    function = forms.CharField(label='Función f(x)', max_length=100)
    a = forms.FloatField(label='Extremo inferior del intervalo (a)')
    b = forms.FloatField(label='Extremo superior del intervalo (b)')
    tolerance = forms.FloatField(label='Tolerancia')
    max_iterations = forms.IntegerField(label='Máx. Iteraciones', initial=100, min_value=1)

#formulario para el metodo de biseccion
class NewtonRaphsonForm(forms.Form):
    function = forms.CharField(label='Función f(x)', max_length=100)
    derivative = forms.CharField(label="Derivada f'(x)", max_length=100)
    initial_guess = forms.FloatField(label='Valor inicial (x₀)')
    tolerance = forms.FloatField(label='Tolerancia')
    max_iterations = forms.IntegerField(label='Máx. Iteraciones', initial=100, min_value=1)

#formulario para el metodo de biseccion
class ModifiedNewtonRaphsonForm(forms.Form):
    function = forms.CharField(label='Función f(x)', max_length=100)
    derivative = forms.CharField(label="Derivada f'(x)", max_length=100)
    second_derivative = forms.CharField(label="Segunda derivada f''(x)", max_length=100)
    initial_guess = forms.FloatField(label='Valor inicial (x₀)')
    tolerance = forms.FloatField(label='Tolerancia')
    max_iterations = forms.IntegerField(label='Máx. Iteraciones', initial=100, min_value=1)


