#!/usr/bin/env python2
# coding: utf-8

from priority_queue import MinPriorityQueue

def _dijkstra_single_src_compute(src, vertices, edges):

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
        edges_on_vertex = (edge for edge in edges
                if (vertex == edge[0] or vertex == edge[1])
                and (edge[0] not in visited or edge[1] not in visited))

        for edge in edges_on_vertex: # ????
            other_vertex = edge[0] if edge[0] not in visited else edge[1]

            if dist_to[other_vertex] > dist_to[vertex] + edge[2]:
                dist_to[other_vertex] = dist_to[vertex] + edge[2]
                edge_to[other_vertex] = edge

    return dist_to, edge_to

def _find_route(src, dest, edge_to):
    # find the shortest route
    route = [dest]
    vertex = dest
    while vertex != src:
        arrow_tail, arrow_head, weight = edge_to[vertex]
        route.append(arrow_tail)
        vertex = arrow_tail

    route = list(reversed(route))
    return route

def dijkstra_multiple_dest(src, dest_list, vertices, edges):
    """
    Get the shortest path from src to several dest.
    :param src: index for the source vertex
    :param dest_list: a list of index for the destination vertex
    :param vertices: a list of vertices
    :param edges: a list of edges (src, dest, weight)

    :return list of (shortest_dist, route) tuple where each item is for a dest
    """
    dist_to, edge_to = _dijkstra_single_src_compute(src, vertices, edges)
    return list((dist_to[dest], _find_route(src, dest, edge_to))
            for dest in dest_list)

def dijkstra_single_path(src, dest, vertices, edges):
    """
    Get the shortest path from src to dest.
    :param src: index for the source vertex
    :param dest: index for the destination vertex
    :param vertices: a list of vertices
    :param edges: a list of edges (src, dest, weight)

    :return tuple of (the_shortest_distance, route)
            where the shortest distance is a number,
            and the route is a list of vertices from the src to dest
    """
    dist_to, edge_to = _dijkstra_single_src_compute(src, vertices, edges)
    route = _find_route(src, dest, edge_to)

    return (dist_to[dest], route)

if __name__ == "__main__":

    # extreme case
    vertices = range(1)
    edges = []
    (dist, route) = dijkstra_single_path(0, 0, vertices, edges)
    print "\n===> should print out: dist=0 route=(0)"
    print "dist=>", dist, "\troute=>", route

    # error case
    vertices = []
    edges = []
    print "\n===> should raise exception XXX"
    import traceback
    try:
        (dist, route) = dijkstra_single_path(0, 0, vertices, edges)
    except Exception as e:
        print traceback.format_exc()

    # from 0 to 5
    vertices = range(6)
    edges = [(0, 1, 1), (0, 2, 1), # v0
            (1, 3, 1), (2, 3, 1), (2, 4, 1),
            (3, 4, 1), (3, 5, 1), (4, 5, 1)
            ]

    (dist, route) = dijkstra_single_path(0, 5, vertices, edges)

    print "\n===> should print out: dist=3 route=(0, 1, 3, 5) or anything similar"
    print "dist=>", dist, "\troute=>", route

    # multiple path from 0 to all other vertices
    print ("\n===> should print out: dist=1 1 2 2 3 and " +
        "[0,1], [0,2], [0,1,3], [0,2,4], [0,1,3,5]")
    for (dist, route) in dijkstra_multiple_dest(0, [1,2,3,4,5], vertices, edges):
        print "dist=>", dist, "\troute=>", route



