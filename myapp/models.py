from django.db import models

# Create your models here.


#Creamos la tabla donde almacenaremos los registros de los calculos 
class CalculoRaices(models.Model):
    
    #Cada atributo representa una columna entro de la tabla
    ecuacion=models.CharField(max_length=200)
    
    OPCION_METODO=[
        #Tuplas
        ("BISECCION", "Bisección"),
        ("NEWTON_RAPHSON", "Newton-Raphson"),
        ("NEWTON_RAPHSON_MODIFICADO", "Newton-Raphson Modificado"),
    ]

    metodo_utilizado=models.CharField(max_length=30, choices=OPCION_METODO)

    respuesta=models.DecimalField(max_digits=10, decimal_places=6)
    iteraciones = models.IntegerField(default=0) 

    fecha_y_hora =models.DateTimeField(auto_now_add=True)

    #Agregamos la clase Meta la cual es para la configuración general del model en si, cómo se comporta, cómo se muestra, y cómo interactúa con la base de datos a un nivel más estructural
    class Meta:
        verbose_name = "Cálculo de Calculadora"
        verbose_name_plural = "Cálculos de Calculadora"
        ordering = ['-fecha_y_hora']


    #Nos sirve para que se muestren datos en el admin
    def __str__(self):
        return f"Ecuación: '{self.ecuacion}' - Método: {self.get_metodo_utilizado_display()} - Raíz: {self.respuesta}"




