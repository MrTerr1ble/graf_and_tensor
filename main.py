import random
import time
import tracemalloc
import h5py


def count_memory_and_speed(func):
    def wrapper(*args, **kwargs):
        print()
        begin_time = time.time()
        tracemalloc.start()

        result = func(*args, **kwargs)

        end_time = time.time()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print(f"Время выполнения: {round(end_time - begin_time, 4)} секунд")
        print(f"Использованная память: {round(peak / 1024, 4)} Кб\n")

        return result

    return wrapper


@count_memory_and_speed
def generate_random_binary_tree_hdf5(nodes_count, filename):
    with h5py.File(filename, 'w') as f:
        root_group = f.create_group('root')
        node_queue = [(root_group, 0)]
        node_count = 0

        while node_queue and node_count < nodes_count:
            current_group, depth = node_queue.pop(0)
            value = random.randint(0, 1000)
            current_group.attrs['value'] = value
            node_count += 1

            if node_count < nodes_count:
                left_group = current_group.create_group('left')
                node_queue.append((left_group, depth + 1))
                node_count += 1

            if node_count < nodes_count:
                right_group = current_group.create_group('right')
                node_queue.append((right_group, depth + 1))
                node_count += 1

    print(
        f"Сгенерировано случайное бинарное дерево с {nodes_count} "
        f"вершинами и сохранено в файл '{filename}'."
    )


@count_memory_and_speed
def generate_user_defined_binary_tree_hdf5(nodes_count, filename):
    if nodes_count > 10:
        print("Ошибка: количество вершин не должно превышать 10.")
        return

    with h5py.File(filename, 'w') as f:
        root_group = f.create_group('root')
        node_queue = [(root_group, 0)]
        node_count = 0

        while node_queue and node_count < nodes_count:
            current_group, depth = node_queue.pop(0)
            value = int(input(f"Введите значение для узла {node_count + 1}: "))
            current_group.attrs['value'] = value
            node_count += 1

            if node_count < nodes_count:
                choice = input(
                    "Создать левый дочерний "
                    f"узел для узла {node_count}? (y/n):"
                )
                if choice.lower() == 'y':
                    left_group = current_group.create_group('left')
                    node_queue.append((left_group, depth + 1))

            if node_count < nodes_count:
                choice = input(
                    "Создать правый дочерний "
                    f"узел для узла {node_count}? (y/n): "
                )
                if choice.lower() == 'y':
                    right_group = current_group.create_group('right')
                    node_queue.append((right_group, depth + 1))

    print(
        f"Создано бинарное дерево с {nodes_count} "
        f"вершинами и сохранено в файл '{filename}'."
    )


@count_memory_and_speed
def print_tree_hdf5(file_path):
    def display_node(group, level=0, is_left=None):
        if 'value' in group.attrs:
            value = group.attrs['value']
            print('    ' * level, end='')
            if is_left is None:
                prefix = ''
            elif is_left:
                prefix = '└── '
            else:
                prefix = '├── '
            print(prefix + str(value))

        if 'left' in group:
            display_node(group['left'], level + 1, is_left=True)
        if 'right' in group:
            display_node(group['right'], level + 1, is_left=False)

    def count_nodes(group):
        count = 1
        if 'left' in group:
            count += count_nodes(group['left'])
        if 'right' in group:
            count += count_nodes(group['right'])
        return count

    with h5py.File(file_path, 'r') as f:
        root_group = f['root']
        total_nodes = count_nodes(root_group)
        if total_nodes > 20:
            find_max_non_leaf_value(file_path)
        else:
            display_node(root_group)


@count_memory_and_speed
def find_max_non_leaf_value(file_path):
    def traverse(group):
        max_value = float('-inf')
        if 'value' in group.attrs:
            max_value = max(max_value, group.attrs['value'])
        if 'left' in group or 'right' in group:  # Узел не является листом
            if 'left' in group:
                max_value = max(max_value, traverse(group['left']))
            if 'right' in group:
                max_value = max(max_value, traverse(group['right']))
        return max_value

    with h5py.File(file_path, 'r') as f:
        root_group = f['root']
        max_value = traverse(root_group)
        print(
            "Максимальное значение среди внутренних вершин дерева:",
            max_value
        )


@count_memory_and_speed
def convert_hdf5_to_txt(hdf5_file_path, txt_file_path):
    def traverse_and_collect(group):
        nodes = []
        if 'value' in group.attrs:
            nodes.append(group.attrs['value'])
        if 'left' in group:
            nodes.extend(traverse_and_collect(group['left']))
        if 'right' in group:
            nodes.extend(traverse_and_collect(group['right']))
        return nodes

    with h5py.File(hdf5_file_path, 'r') as f:
        root_group = f['root']
        nodes = traverse_and_collect(root_group)

    with open(txt_file_path, 'w') as f:
        for value in nodes:
            f.write(str(value) + '\n')

    print(f"Данные из {hdf5_file_path} успешно записаны в {txt_file_path}")


def generate_and_save():
    n = int(input("Количество вершин: "))
    filename = input("Введите название файла (с расширением .h5): ")

    print("Генерация дерева")
    generate_random_binary_tree_hdf5(n, filename)

    print("Сохранение дерева в файл")
    find_max_non_leaf_value(filename)


def main():
    while True:
        choice = int(input("""\nВыберите действие:
1. Выбрать определенный файл
2. Сгенерировать новое дерево и сохранить его в файл
3. Конвертировать HDF5 файл в текстовый файл
4. Ввести бинарное дерево с клавиатуры
5. Выход
Выбор: """))

        if choice == 1:
            filename = input("Введите название файла (с расширением .h5): ")
            find_max_non_leaf_value(filename)
            print_tree_hdf5(filename)
        elif choice == 2:
            generate_and_save()
        elif choice == 3:
            hdf5_filename = input(
                "Введите название HDF5 файла (с расширением .h5): "
            )
            txt_filename = input(
                "Введите название текстового файла (с расширением .txt): "
            )
            convert_hdf5_to_txt(hdf5_filename, txt_filename)
        elif choice == 4:
            n = int(input("Количество вершин (не более 10): "))
            filename = input("Введите название файла (с расширением .h5): ")
            generate_user_defined_binary_tree_hdf5(n, filename)
        elif choice == 5:
            break
        else:
            print("Несуществующий вариант")


if __name__ == "__main__":
    main()
