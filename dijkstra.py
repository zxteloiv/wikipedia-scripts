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
    dist_to = [None] * len(vertices)
    edge_to = [None] * len(vertices)
    pq = MinPriorityQueue()

    visited = set()

def _visit(dist_to, edge_to):
    pass

