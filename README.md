# Calefacción Inteligente
Se entrenará un agente mediante aprendizaje por refuerzo en un entorno personalizado, donde deberá mantener la temperatura de una habitación lo más cercana posible a un valor objetivo, utilizando la menor cantidad de energía.

El agente podrá encender o apagar la calefacción, observando la temperatura actual, la temperatura exterior y la deseada.
Las recompensas se diseñarán en función de dos factores principales:

## Confort térmico:
Penalizando la desviación entre la temperatura actual y la temperatura objetivo, si el agente puede llegar a una temperatura objetivo cercana o igual se lo recompensará.

## Eficiencia energética:
Penalizando el uso excesivo de la calefacción, solo se debe enviar la cantidad suficiente de calor o de frio para alcanzar la temperatura deseada, sin gastar energia de mas.

De esta forma, el agente aprenderá una política óptima que equilibre el confort y el ahorro energético, simulando el comportamiento de un sistema inteligente de climatización doméstico.
