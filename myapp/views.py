import matplotlib #Para la grafica 
matplotlib.use('Agg')
from django.shortcuts import render #para cargar los archivo html y pasarle los datos
from sympy import sympify, Symbol, lambdify #Para realizar calculos matemáticos
import numpy as np
from decimal import Decimal
from .forms import BisectionForm, NewtonRaphsonForm, ModifiedNewtonRaphsonForm #Importamos los forms de cada metodo

from .models import CalculoRaices #Importamos el models

#Para convertir la grafica a imagen 
import matplotlib.pyplot as plt
import io
import base64

#Para mostrar los datos de la base de datos en el home
def home(request):
    calculos_anteriores = CalculoRaices.objects.all().order_by('-id')
    #Creamos un diccionarion con todos los calculos y renderiza la plantilla html para que se muestre los datos
    context = {
        'calculos': calculos_anteriores
    }
    return render(request, 'home.html', context)


def bisection_view(request):
    #inicializamos el form correspondiente
    form = BisectionForm()
    #Definimos las variables que vamos autilizar
    result = None
    iterations = None
    error = None
    plot_base64 = None
    #Lista para guardar los datos de cada iteración
    iterations_data = []

    #Si la solicitud es POST (el usuario ha enviado el formulario)
    if request.method == 'POST':
        
        #Le enviamos la información del usuario al formulario y lo guardamos dentro del objeto form
        form = BisectionForm(request.POST)

        #Si los datos del formulario son valido
        if form.is_valid():
            data = form.cleaned_data
            #Extraemos la información como cadera
            function_str = data['function']
            a, b = data['a'], data['b']
            tol = data['tolerance']
            max_iterations = data['max_iterations'] 

            try:
                #Utilizamos sympy para convertir la cadena de la función en una expresión simbólica y luego en una función evaluable
                x = Symbol('x')
                f_expr = sympify(function_str)
                f = lambdify(x, f_expr, 'numpy')

                # Listas para almacenar los puntos de las iteraciones para la gráfica
                x_history = []
                y_history = []

                #Verificamos si cambia de sirvo en el intervalo dado
                if f(a) * f(b) >= 0:
                    error = "La función no cambia de signo en el intervalo dado [a, b]."
                else:
                    c = 0.0
                    current_iterations = 0

                    for i in range(max_iterations):
                        current_iterations = i + 1
                        c = (a + b) / 2

                        #Guardamos los datos relevantes en interacions_data para mostrarlos en una tabla en la plantilla
                        iterations_data.append({
                            'iteration': current_iterations,
                            'a': f"{a:.6f}",
                            'b': f"{b:.6f}",
                            'c': f"{c:.6f}",
                            'f_c': f"{f(c):.6f}",
                            'error_approx': f"{abs(b - a) / 2:.6f}"
                        })

                        x_history.append(c)
                        y_history.append(f(c))

                        #Si el resultado es cero o el error es menor al tolerado entonces se considera que se encontro la raiz y se sale del bucle
                        if f(c) == 0.0 or abs(b - a) / 2 < tol:
                            result = c
                            iterations = current_iterations
                            break

                        #Actualizamos el intervalo basandose en el signo de f(c)
                        if f(c) * f(a) < 0:
                            b = c
                        else:
                            a = c
                    else:
                        #Si no se encuentra al recorrer todas las iteraciones
                        error = f"El método no convergió en {max_iterations} iteraciones."
                        result = c
                        iterations = current_iterations

                #Si encuentra la raiz y no hay errores    
                if result is not None and error is None:
                    #Guardamos los calculos en el model CalculoRaices
                    try:
                        CalculoRaices.objects.create(
                            ecuacion=function_str,
                            metodo_utilizado="BISECCION",
                            respuesta=Decimal(str(result)),
                            iteraciones=iterations
                        )
                        
                    #Para el manejo de excepciones
                    except Exception as db_error:
                        error = f"Error al guardar el resultado en la base de datos: {db_error}"

                    #Generamos la grafica usando motplolib
                    try:
                        plt.figure(figsize=(8, 6))
                        plot_min_x = min(data['a'], data['b'], float(result)) - 1
                        plot_max_x = max(data['a'], data['b'], float(result)) + 1
                        if abs(plot_max_x - plot_min_x) < 0.1:
                            plot_min_x -= 0.5
                            plot_max_x += 0.5
                            
                        x_vals = np.linspace(plot_min_x, plot_max_x, 400)
                        y_vals = f(x_vals)

                        #Para dibujar la funcion
                        plt.plot(x_vals, y_vals, label=f'f(x) = {function_str}', color='blue')
                        plt.axhline(0, color='gray', linewidth=0.8, linestyle='--')

                        if result is not None:
                            #Dibujar la raiz
                            plt.axvline(x=float(result), color='red', linestyle='--', label=f'Raíz: {float(result):.6f}')
                            #Marcar con un punto en la raiz
                            plt.scatter([float(result)], [f(float(result))], color='red', zorder=5, marker='o', s=100)

                        #Titulos en la grafica
                        plt.grid(True)
                        plt.legend()
                        plt.title('Gráfica del Método de Bisección')
                        plt.xlabel('x')
                        plt.ylabel('f(x)')

                        #Guardar el grafico en un buffer de memoria como una imagen png
                        buffer = io.BytesIO()
                        plt.savefig(buffer, format='png')
                        buffer.seek(0)
                        #Codifica la imagen en Base64 para poder incrustarla en el html
                        plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        plt.close()

                    #Para el manejo de excepciones
                    except Exception as plot_error:
                        plot_base64 = None
                        if error:
                            error += f"\nError al generar la gráfica: {plot_error}"
                        else:
                            error = f"Error al generar la gráfica: {plot_error}"
                else:
                    plot_base64 = None

            #Para el manejo de excepciones
            except SyntaxError:
                error = "Error de sintaxis en la función."
                plot_base64 = None
            except NameError:
                error = "Error: variable no definida en la función (ej. usa 'x' en lugar de otra letra)."
                plot_base64 = None
            except TypeError as e:
                error = f"Error de tipo al evaluar la función. Asegúrate de usar la sintaxis correcta (ej. 'x**2' para $x^2$, 'np.exp(x)' para $e^x$, 'np.cos(x)' para coseno): {e}."
                plot_base64 = None
            except Exception as e:
                error = f"Error inesperado al evaluar la función o realizar el cálculo: {e}"
                plot_base64 = None

    #Renderiza la plantilla del archivo html pasando el fomulario y los resultados
    return render(request, 'bisection.html', {
        'form': form,
        'result': result,
        'iterations': iterations,
        'error': error,
        'plot_base64': plot_base64,
        'iterations_data': iterations_data 
    })


def newton_raphson_view(request):
    from sympy import diff
    #Inicializamos el form correspondiente
    form = NewtonRaphsonForm()
    result = None
    iterations = None
    error = None
    plot_base64 = None
    #Lista para guardar los datos de cada iteración
    iterations_data = []
    

    #Si la solicitud es POST (el usuario ha enviado el formulario)
    if request.method == 'POST':
        
        #Le enviamos la información del usuario al formulaio y lo guardamos dentro del objeto del form
        form = NewtonRaphsonForm(request.POST)

        #Si los datos del formulario son validos
        if form.is_valid():
            data = form.cleaned_data
            #Extraemos la información como validos
            function_str = data['function']
            derivative_str = data['derivative']
            max_iterations = data['max_iterations'] 

            try:
                #Utilizamos sympy para convertir la cadena de la función en una expresión simbólica y luego en una función evaluable
                x = Symbol('x')
                f_expr = sympify(function_str)
                f = lambdify(x, f_expr, 'numpy')
                df_expr = sympify(derivative_str)
                df = lambdify(x, df_expr, 'numpy')

                x0 = float(data['initial_guess'])
                tol = float(data['tolerance'])

                current_iterations = 0

                # Para la gráfica y la tabla de iteraciones
                x_history = [x0] # Solo para la gráfica
                y_history = [f(x0)] # Solo para la gráfica

                #Guardamos los datos relevantes en interacions_Data para mostrarlos en una tabla en la plantilla
                initial_f_val = f(x0)
                iterations_data.append({
                    'iteration': 0, # Iteración inicial
                    'x_n': f"{x0:.6f}",
                    'f_x_n': f"{initial_f_val:.6f}",
                    'df_x_n': f"{df(x0):.6f}", 
                    'error_approx': '-' 
                })


                for i in range(max_iterations):
                    current_iterations = i + 1
                    f_val = f(x0)
                    df_val = df(x0)

                    if abs(df_val) < 1e-10:
                        error = "La derivada es demasiado cercana a cero, el método no puede continuar."
                        break
                    
                    x1 = x0 - f_val / df_val
                    
                    # Calcula el error de aproximación para esta iteración
                    error_approx_val = abs(x1 - x0)

                    #Guarda los datos de la iteración
                    iterations_data.append({
                        'iteration': current_iterations,
                        'x_n': f"{x1:.6f}",
                        'f_x_n': f"{f(x1):.6f}",
                        'df_x_n': f"{df(x1):.6f}",
                        'error_approx': f"{error_approx_val:.6f}"
                    })

                    x_history.append(x1)
                    y_history.append(f(x1))

                    #Si el error aproximado es menor al tolerable, se considera que ya se encontro la raiz y termina el bucle
                    if error_approx_val < tol: 
                        result = x1
                        iterations = current_iterations
                        break
                    x0 = x1
                else:
                    #Si no se encontro al recorrer todas las iteraciones
                    error = f"El método no convergió en {max_iterations} iteraciones."
                    result = x0
                    iterations = current_iterations

                #Si encuentra la raiz y no hay errores
                if result is not None and error is None:
                    #Guardamos los calculos en el model Calculo Raices
                    try:
                        CalculoRaices.objects.create(
                            ecuacion=function_str,
                            metodo_utilizado="NEWTON_RAPHSON",
                            respuesta=Decimal(str(result)),
                            iteraciones=iterations
                        )

                    #Para el manejo de excepciones    
                    except Exception as db_error:
                        error = f"Error al guardar el resultado en la base de datos: {db_error}"

                    #Generamos la grafica 
                    try:
                        min_x = min(x_history) - 1
                        max_x = max(x_history) + 1
                        if result is not None:
                            min_x = min(min_x, float(result)) - 1
                            max_x = max(max_x, float(result)) + 1
                        if abs(max_x - min_x) < 0.1:
                            min_x -= 0.5
                            max_x += 0.5

                        x_vals = np.linspace(min_x, max_x, 400)
                        y_vals = f(x_vals)

                        #Dibujar la funcion
                        plt.figure(figsize=(8, 6))
                        plt.plot(x_vals, y_vals, label=f'f(x) = {function_str}')
                        plt.axhline(0, color='gray', linewidth=0.8) 
                        
                        if result is not None:
                           #Dibujar la raiz
                           plt.axvline(x=float(result), color='r', linestyle='--', label=f'Raíz: {float(result):.6f}')
                           #Marcar el punto en la raiz
                           plt.scatter([float(result)], [f(float(result))], color='red', zorder=5, marker='o', s=100)                            
                        
                        #Titulos en la grafica
                        plt.grid(True)
                        plt.legend()
                        plt.title('Gráfica del Método de Newton-Raphson')
                        plt.xlabel('x')
                        plt.ylabel('f(x)')

                        #Guardamos el grafico en un buffer de memoria como una imagen png
                        buffer = io.BytesIO()
                        plt.savefig(buffer, format='png')
                        buffer.seek(0)
                        #Codifica la imagen en Base 64 para poder incrustarla en el html 
                        plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        plt.close() 

                    #Para el manejo de excepciones
                    except Exception as plot_error:
                        plot_base64 = None 
                        if error: 
                            error += f"\nError al generar la gráfica: {plot_error}"
                        else: 
                            error = f"Error al generar la gráfica: {plot_error}"
                else:
                    plot_base64 = None 

            #Para el manejo de excepciones
            except SyntaxError:
                error = "Error de sintaxis en la función o derivada."
                plot_base64 = None
            except NameError:
                error = "Error: variable no definida en la función o derivada."
                plot_base64 = None
            except TypeError as e:
                error = f"Error de tipo en la función o derivada: {e}."
                plot_base64 = None
            except Exception as e:
                error = f"Error inesperado al evaluar las funciones o realizar el cálculo: {e}"
                plot_base64 = None

    #Renderiza la plantilla del archivo html pasano el formulario y los resultados
    return render(request, 'newton_raphson.html', {
        'form': form, 
        'result': result, 
        'iterations': iterations, 
        'error': error,
        'plot_base64': plot_base64,
        'iterations_data': iterations_data 
    })


def modified_newton_raphson_view(request):
    from sympy import diff 
    #Inicializamos el form correspondiente 
    form = ModifiedNewtonRaphsonForm()
    #Definimos las variables que vamos a utilizar
    result = None
    iterations = None
    error = None
    plot_base64 = None
    #Lista para guardar los datos de cada iteracion 
    iterations_data = [] 

    #Si la solicitud es POST (el usuario ha enviao el formulario)
    if request.method == 'POST':

        #Le enviamos la información del usuario al formulario y lo guardamos dentro del objeto form
        form = ModifiedNewtonRaphsonForm(request.POST)

        #Si los datos del formulario son validos
        if form.is_valid():
            data = form.cleaned_data
            #Extraemos la información como cadena
            function_str = data['function']
            derivative_str = data['derivative']
            second_derivative_str = data['second_derivative']
            max_iterations = data['max_iterations'] 

            try:
                #Utilizamos sympy para convertir la cadena de la función en una expresión simbólica y luego en una función evaluable
                x = Symbol('x')
                f_expr = sympify(function_str)
                f = lambdify(x, f_expr, 'numpy')
                df_expr = sympify(derivative_str)
                df = lambdify(x, df_expr, 'numpy')
                d2f_expr = sympify(second_derivative_str)
                d2f = lambdify(x, d2f_expr, 'numpy')

                x0 = float(data['initial_guess'])
                tol = float(data['tolerance'])

                current_iterations = 0

                #Para la grafica
                x_history = [x0]
                y_history = [f(x0)] 

                # Primer punto para la tabla de iteraciones
                initial_f_val = f(x0)
                iterations_data.append({
                    'iteration': 0,
                    'x_n': f"{x0:.6f}",
                    'f_x_n': f"{initial_f_val:.6f}",
                    'df_x_n': f"{df(x0):.6f}",
                    'd2f_x_n': f"{d2f(x0):.6f}",
                    'error_approx': '-'
                })

                #Bucle para realizar las iteraciones
                for i in range(max_iterations):
                    current_iterations = i + 1
                    f_val = f(x0)
                    df_val = df(x0)
                    d2f_val = d2f(x0)

                    #Si el denominador es demasiado cercano a cero
                    denominator = (df_val**2) - (f_val * d2f_val)
                    if abs(denominator) < 1e-10:
                        error = "El denominador es demasiado cercano a cero."
                        break
                    
                    x1 = x0 - (f_val * df_val) / denominator
                    error_approx_val = abs(x1 - x0)

                    #Guarda los datos de la iteración
                    iterations_data.append({
                        'iteration': current_iterations,
                        'x_n': f"{x1:.6f}",
                        'f_x_n': f"{f(x1):.6f}",
                        'df_x_n': f"{df(x1):.6f}",
                        'd2f_x_n': f"{d2f(x1):.6f}",
                        'error_approx': f"{error_approx_val:.6f}"
                    })

                    x_history.append(x1)
                    y_history.append(f(x1))

                    #Si el error aproximado es menor al tolerado se considera que ya se encontro la raiz y se termina el bucle
                    if error_approx_val < tol:
                        result = x1
                        iterations = current_iterations
                        break
                    x0 = x1
                else:
                    #Si no se encontro al recorrer todas las iteraciones
                    error = f"El método no convergió en {max_iterations} iteraciones."
                    result = x0
                    iterations = current_iterations

                #Si encontra la raiz y no hay errores
                if result is not None and error is None:
                    #Gurdamos los calculos en el model CalculoRaices
                    try:
                        CalculoRaices.objects.create(
                            ecuacion=function_str,
                            metodo_utilizado="NEWTON_RAPHSON_MODIFICADO",
                            respuesta=Decimal(str(result)),
                            iteraciones=iterations
                        )
                    #Para el manejo de excepciones
                    except Exception as db_error:
                        error = f"Error al guardar el resultado en la base de datos: {db_error}"

                    #Generamos la grafica
                    try:
                        min_x = min(x_history) - 1
                        max_x = max(x_history) + 1
                        if result is not None:
                            min_x = min(min_x, float(result)) - 1
                            max_x = max(max_x, float(result)) + 1
                        if abs(max_x - min_x) < 0.1:
                            min_x -= 0.5
                            max_x += 0.5

                        x_vals = np.linspace(min_x, max_x, 400)
                        y_vals = f(x_vals)

                        #Para dibujar la funcion
                        plt.figure(figsize=(8, 6))
                        plt.plot(x_vals, y_vals, label=f'f(x) = {function_str}')
                        plt.axhline(0, color='gray', linewidth=0.8) 
                        
                        if result is not None:
                            #Dibujar la raiz
                            plt.axvline(x=float(result), color='r', linestyle='--', label=f'Raíz: {float(result):.6f}')
                            #Marcar con un punto la raiz
                            plt.scatter([float(result)], [f(float(result))], color='red', zorder=5, marker='o', s=100)

                        #Titulos en la grafica
                        plt.grid(True)
                        plt.legend()
                        plt.title('Gráfica del Método de Newton-Raphson Modificado')
                        plt.xlabel('x')
                        plt.ylabel('f(x)')

                        #Guardar el grafico en un buffer de memoria como una imagen png
                        buffer = io.BytesIO()
                        plt.savefig(buffer, format='png')
                        buffer.seek(0)
                        #Codifica la imagen en Base64 para poder incrustarla en el html
                        plot_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
                        plt.close() 

                    #Para el manejo de excepciones
                    except Exception as plot_error:
                        plot_base64 = None 
                        if error: 
                            error += f"\nError al generar la gráfica: {plot_error}"
                        else: 
                            error = f"Error al generar la gráfica: {plot_error}"
                else:
                    plot_base64 = None 

            #Para el manejo de excepciones
            except SyntaxError:
                error = "Error de sintaxis en la función o derivadas."
                plot_base64 = None
            except NameError:
                error = "Error: variable no definida en la función o derivadas."
                plot_base64 = None
            except TypeError as e:
                error = f"Error de tipo en la función o derivadas: {e}."
                plot_base64 = None
            except Exception as e:
                error = f"Error inesperado al evaluar las funciones o realizar el cálculo: {e}"
                plot_base64 = None

    #Renderiza la plantilla del archivo html pasando el formulario y los resultados
    return render(request, 'modified_newton_raphson.html', {
        'form': form, 
        'result': result, 
        'iterations': iterations, 
        'error': error,
        'plot_base64': plot_base64,
        'iterations_data': iterations_data 
    })

