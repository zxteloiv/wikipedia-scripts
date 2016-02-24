#!/usr/bin/env python2
# coding: utf-8

from priority_queue import MinPriorityQueue

def dijkstra_single_path(src, dest, vertices, edges):
    """
    Get the shortest path from src to dest.
    :param src: index for the source vertex
    :param dest: index for the destination vertex
    :param vertices: a list of vertices
    :param edges: a list of edges (src, dest, weight)
    """

    # init 
    dist_to = [4294967295] * len(vertices)
    edge_to = [None] * len(vertices)
    if len(vertices) == 0:
        raise ValueError('Cannot deal with empty vertex set')
    dist_to[src] = 0

    visited = set()

    pq = MinPriorityQueue(lambda x:dist_to[x])
    for vertex in xrange(len(vertices)):
        pq.insert(vertex)

    # choose a vertex and relax the edges on it, until optimal
    while True:
        vertex = pq.pop()
        if vertex is None: break

        visited.add(vertex)
        # find all edges starting from the vertex, and relax the edge.
        # in an undirect graph, both src and dest of an edge is considered 
        edges_on_vertex = (edge for edge in edges if vertex in edge)

        for edge in edges_on_vertex: # ????
            other_vertex = edge[0] if edge[0] not in visited else edge[1]
            if dist_to[other_vertex] > dist_to[vertex] + edge[2]:
                dist_to[other_vertex] = dist_to[vertex] + edge[2]
                edge_to[other_vertex] = edge

    # find the shortest route
    route = [dest]
    vertex = dest
    while vertex != src:
        arrow_tail, arrow_head, weight = edge_to[vertex]
        route.append(arrow_tail)
        vertex = arrow_tail

    route = list(reversed(route))

    return (dist_to[dest], route)

if __name__ == "__main__":

    vertices = range(6)
    edges = [(0, 1, 1), (0, 2, 1), # v0
            (1, 3, 1), (2, 3, 1), (2, 4, 1),
            (3, 4, 1), (3, 5, 1), (4, 5, 1)
            ]

    (dist, route) = dijkstra_single_path(0, 5, vertices, edges)

    print "should print out: dist=3 route=(0, 1, 3, 5) or anything similar"
    print "dist=>", dist, "\troute=>", route

    # extreme case

    vertices = range(1)
    edges = []
    (dist, route) = dijkstra_single_path(0, 0, vertices, edges)
    print "should print out: dist=0 route=(0)"
    print "dist=>", dist, "\troute=>", route

    # error case
    vertices = []
    edges = []
    print "should raise exception XXX"
    import traceback
    try:
        (dist, route) = dijkstra_single_path(0, 0, vertices, edges)
    except Exception as e:
        print traceback.format_exc()

    # blabla


