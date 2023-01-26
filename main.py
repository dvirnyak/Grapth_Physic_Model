import matplotlib.pyplot as plt
import matplotlib.animation as animation # Для анимации
import random # Для генерации графа
import networkx as nx # Для удобной работы с графами
from colour import Color # Для наглядности напряжений пружинок-рёбер я решил красить рёбра в соответствующие цвета
colors = list(Color("#034d06").range_to(Color("#a60000"), 2000)) # заранее настраиваем градиент для раскраски рёбер

# коэффициенты
weight = 0.0001 # масса одной вершины. При больших массах система очень долго не приходит в равновесие
g = 9800
N = weight * g # вес. Он нужен для закона Амонтона — Кулона ( F = μN )
k_friction = 0.7 # μ для закона Амонтона — Кулона
normal_lenght = 7 # длина условно недеформированной пружины ( ребра графа )
k_guk = 8 # Коэфициент жёсткости пружины(ребра графа)
k_kulon = -60 # Коэфиецент для закона Кулона
interval = 0.001 # условное время между пересчитыванием сил и изменением координат

def current_situation(num, speeds, coordinates, G, ax):#считает силы, изменяет координаты, красит рёбра
    #считаем силы
    forces = []
    for i in range(0, len(coordinates)):
        forces.append([0, 0])
    # считаем силы Кулона
    for i, c in coordinates.items():
        for j, c1 in coordinates.items():
            distance = ( ( c[0] - c1[0] ) ** 2 + ( c[1] - c1[1] ) ** 2 ) ** 0.5 + 0.000000001#чтобы не было деления на 0
            force = k_kulon / (distance ** 2)
            cos = ( c1[0] - c[0] ) / distance # cos вектора силы
            forcex = force * cos
            sin = ( c1[1] - c[1] ) / distance # sin вектора силы
            forcey = force * sin
            forces[i][0] += forcex
            forces[i][1] += forcey
    # Считаем силы Гука
    for i,c in coordinates.items():
        for j,c1 in coordinates.items():
            if G.has_edge(i, j) and i != j:
                distance = ( (c[0] - c1[0]) ** 2 + (c[1] - c1[1]) ** 2 ) ** 0.5 + 0.000000001#чтобы не было деления на 0
                force = k_guk * (distance - normal_lenght)
                cos = (c1[0] - c[0]) / distance  # cos вектора силы
                forcex = force * cos
                sin = (c1[1] - c[1]) / distance # sin вектора силы
                forcey = force * sin
                forces[i][0] += forcex
                forces[i][1] += forcey
    # Силы трения. Учитываем, что сила трения должна именно тормозить тело, а не разгоянть его в противоположном направлении
    for i in coordinates.keys():
        if ((speeds[i][0] ** 2 + speeds[i][1] ** 2) ** 0.5 <= N * k_friction * interval ** 2 / 2): # иначе бы сила трения остановила и начала бы разгонть тело
            speeds[i][0] = 0
            speeds[i][1] = 0
        else:
            # вектор силы трения направлен против направления движения тела
            cos = speeds[i][0] / (speeds[i][0] ** 2 + speeds[i][1] ** 2) ** 0.5  # cos вектора силы трения
            frictionx = N * k_friction * cos
            sin = speeds[i][1] / (speeds[i][0] ** 2 + speeds[i][1] ** 2) ** 0.5  # sin вектора силы трения
            frictiony = N * k_friction * sin
            forces[i][0] -= frictionx
            forces[i][1] -= frictiony
    # print(forces)
    # print(speeds)
    # изменяем координаты
    for j in coordinates.keys():
        accelerationx = forces[j][0] / weight
        accelerationy = forces[j][1] / weight
        x1 = coordinates[j][0] + speeds[j][0] * interval + accelerationx * interval ** 2 / 2 # x1 = x0 + V0x*t + ax*t^2/2
        y1 = coordinates[j][1]+ speeds[j][1] * interval + accelerationy * interval ** 2 / 2 # y1 = y0 + V0y*t + ay*t^2/2
        coordinates[j] = (x1,y1)
    # изменяем скорости
    for i in range(0, len(coordinates)):
        speeds[i][0] += interval * forces[i][0]
        speeds[i][1] += interval * forces[i][1]
    # изменяем цвета рёбер, чтобы показать силу натяжения
    edge_color_list=[]
    for i,j in G.edges():
        distance = ((coordinates[i][0] - coordinates[j][0]) ** 2 + (coordinates[i][1] - coordinates[1][1]) ** 2) ** 0.5 + 0.000000001  # чтобы не было деления на 0
        # считаем порядковый номер цвета в массиве цветов градиента
        # Чем сильнее отличие, тем краснее ребро. Домножил на 250 для разнообразности цветов
        color_i=round((max(distance,normal_lenght) - min(distance,normal_lenght)) * 250)
        if(color_i > 1999):# не выходим за рамки массива
            color_i = 1999
        edge_color_list.append(colors[color_i].hex_l)
    # чистим старый рисунок и рисуем новый
    ax.clear()
    nx.draw(G, pos=coordinates, edge_color = edge_color_list, ax=ax)

# генерим граф с рандомным количеством вершин и рандомными рёбрами
G = nx.Graph()# объявляем граф
coordinates = {}
for i in range(random.randint(7, 23)):
    coordinates[i] = (random.uniform(0, 100), random.uniform(0, 100))
G.add_nodes_from(coordinates.keys())

for i in coordinates.keys():
    number_of_edges = random.randint(2, len(coordinates.keys()) - 1)
    if number_of_edges <= len(G.edges(i)) or number_of_edges>=len(coordinates.keys()) - 1: # если рёбер для данной вершины достаточно
        continue
    for j in range(number_of_edges):
        i1 = random.randint(0, len(coordinates.keys())-1)
        while (i1 == i or G.has_edge(i, i1)) and number_of_edges >= len(G.edges(i)): # Найдём вершину, к которой можно провести ребро
            i1 = random.randint(0, len(coordinates.keys()) - 1) # с изначальной вершиной что-то было не так, и мы выбрали новую
        G.add_edge(i, i1) # добавим ребро
# изначальные скорости равны 0
speeds = []
for i in range(len(coordinates)):
    speeds.append([0, 0])
# анимируем граф
fig, ax = plt.subplots(figsize=(7, 5))
ani = animation.FuncAnimation(fig, current_situation, interval=1,frames=100000, fargs=(speeds, coordinates, G,ax))
plt.show() # Выводим на экран результат
