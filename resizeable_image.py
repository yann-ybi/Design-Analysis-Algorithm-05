import imagematrix

class Node:
    """
    Represents a node in a linked list of pixels in an image.
    """
    def __init__(self, pixel, prev, next):
        self.pixel = pixel
        self.prev = prev
        self.next = next

class Path:
    """
    Represents a path between two nodes in a graph.
    """
    def __init__(self, root: Node, energy, end: Node, len):
        self.root = root
        self.energy = energy
        self.end = end
        self.len = len

class ResizeableImage(imagematrix.ImageMatrix):
    def best_seam(self, dp=True) -> list[tuple]:
        """
        Returns the best vertical seam to remove from the image using either the dynamic programming or greedy algorithm.
        :param dp: if True, uses dynamic programming algorithm; if False, uses greedy algorithm.
        :return: list of tuples representing the pixels that make up the best vertical seam.
        """
        return self.dp_seam() if dp else self.gd_seam()

    def remove_best_seam(self):
        self.remove_seam(self.best_seam())

    def dp_seam(self) -> list:
        """
        finds the minimum energy seam path in the image using dynamic programming.
        :returns: a list of tuples representing the pixels in the minimum energy seam path.
        """
        # Get the minimum energy path for each pixel
        cells = self.dynamic()
        j = 0
        node = Node((0, 0), None, None)
        path = Path(node, cells[(0, 0)], node, 1)
        result = []

        # Find cell with the minimum energy path for each pixel in the first row
        for i in range(1, self.width):
            enrg = cells[(i, j)]
            if enrg < path.energy:
                path.root.pixel = (i, j)
                path.energy = enrg
                path.end.pixel = (i, j)
        result.append(path.end.pixel)

        # Construct the minimum energy seam path from top to bottom from that cell
        while path.end.pixel[1] != self.height - 1:
            nxts = [None, None , None]
            (i, j) = path.end.pixel
            nxts = self.nexts(i, j)
            iter_cell = nxts[0]
            iter_enrg = cells[iter_cell] if nxts else None
            
            for cell in nxts[1:]:
                enrg = cells[cell]
                if enrg < iter_enrg:
                    iter_cell = cell
                    iter_enrg = enrg

            path.end.next = Node(iter_cell, path.end, None)
            path.end = path.end.next
            path.len += 1
            result.append(path.end.pixel)
        return result
    
    def gd_seam(self) -> list[tuple]:
        """
        finds the optimal vertical seam to remove from the image using the Greedy / Naive algorithm.
        :returns: list of tuples representing the pixels that make up the optimal vertical seam.
        """
        penergies = dict()
        paths: list[Path] =  []
        j = 0
        # Compute the energy of each pixel. Create a new Node object to represent the current pixel and a new Path object with the current pixel as its root, end, and length of 1.
        for i in range(0, self.width):
            energy = self.energy(i, j)
            node = Node((i,j), None, None)
            path = Path(node, energy, node, 1)
            paths.append(path)
            penergies[(i, j)] = energy

        # For each pixel, find the next set of adjacent pixels that can be added to the current path.
        for path in paths:
            (i, j) = path.end.pixel
            nxt_cells = self.nexts(i, j)
            # If there are no more adjacent pixels to add, the seam has reached the bottom of the image.
            if not nxt_cells:
                results = [path for path in paths if path.len == self.height]
                best_path = min(results, key=lambda p: p.energy)
                result = []
                while best_path.end is not None:
                    result = [best_path.end.pixel] + result
                    best_path.end = best_path.end.prev
                return result
            
            # for each pixel, if there are still adjacent pixels to add, create a new Path for it.
            for (ni, nj) in nxt_cells:
                new_path = Path(path.root, path.energy, path.end, path.len)
                new_path.end.next = Node((ni, nj), path.end, None)
                new_path.end = new_path.end.next
                new_path.len += 1

                energy = penergies[(ni, nj)] if (ni, nj) in penergies.keys() else self.energy(ni, nj)
                penergies[(ni, nj)] = energy
                new_path.energy += energy
                paths.append(new_path)
    
    def dynamic(self) -> dict:
        """
        calculates the minimum energy path from each pixel to bottom.
        :returns: dictionary with the coordinate of the pixel and energy
        """
        penergies = dict()
        min_energy_path = dict()
        for h in range(1, self.height + 1):
            for i in range(0, self.width):
                j = self.height - h

                if (i, j) not in penergies.keys():
                    energy = self.energy(i, j)
                    penergies[(i, j)] = energy
                else: 
                    energy = penergies[(i, j)]
                prevs = self.nexts(i, j)

                if prevs:
                    enrgs = [min_energy_path[(i, j)] for (i, j) in prevs]
                    min_energy = min(enrgs)
                    min_energy_path[(i, j)] = energy + min_energy
                else:
                    min_energy_path[(i, j)] = energy    
        return min_energy_path

    def nexts(self, i: int, j: int) -> list:
        """
        returns a list of tuples representing the coordinates of the adjacent cells
        of the current cell with coordinates (i, j).
        :param i: int, the row index of the current cell
        :param j: int, the column index of the current cell
        :return: list of tuples, each tuple representing the coordinates of an adjacent cell
        """
        nxt_cells = [None, None , None]
        nxt_cells[0] = (i - 1, j + 1) if i - 1 > 0 and j + 1 < self.height else None
        nxt_cells[1] = (i, j + 1) if j + 1 < self.height else None
        nxt_cells[2] = (i + 1, j + 1) if i + 1 < self.width and j + 1 < self.height else None
        nxt_cells = [x for x in nxt_cells if x is not None]
        return nxt_cells
    