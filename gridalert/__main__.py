import argparse
from logging import basicConfig, INFO

from .gridalert import *

# logger
basicConfig(level=INFO,
            format='%(asctime)s [%(levelname)-7s] %(message)s')


def command_text(args):
    ga = GridAlert(args.conf, args.option)
    ga.text_to_db()

def command_label(args):
    ga = GridAlert(args.conf, args.option)
    ga.labeling()

def command_vector(args):
    ga = GridAlert(args.conf, args.option)
    ga.vectorize()

def command_cluster(args):
    ga = GridAlert(args.conf, args.option)
    ga.clustering()

def command_plot(args):
    ga = GridAlert(args.conf, args.option)
    ga.plot()

def command_cherrypy(args):
    ga = GridAlert(args.conf, args.option)
    ga.visualize()

def command_html(args):
    ga = GridAlert(args.conf, args.option)
    ga.html()

def command_alert(args):
    ga = GridAlert(args.conf, args.option)
    ga.alert()

def command_all(args):
    ga = GridAlert(args.conf, args.option)
    ga.text_to_db()
    ga.vectorize()
    ga.clustering()
    ga.plot()
    ga.alert()


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
   
    # text
    parser_text = subparsers.add_parser('text')
    parser_text.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_text.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_text.set_defaults(handler=command_text) 

    # label
    parser_label = subparsers.add_parser('label')
    parser_label.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_label.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_label.set_defaults(handler=command_label) 

    # vector
    parser_vector = subparsers.add_parser('vector')
    parser_vector.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_vector.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_vector.set_defaults(handler=command_vector) 

    # cluster
    parser_cluster = subparsers.add_parser('cluster')
    parser_cluster.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_cluster.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_cluster.set_defaults(handler=command_cluster) 

    # plot
    parser_plot = subparsers.add_parser('plot')
    parser_plot.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_plot.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_plot.set_defaults(handler=command_plot) 
 
    # cherrypy
    parser_cherrypy = subparsers.add_parser('cherrypy')
    parser_cherrypy.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_cherrypy.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_cherrypy.set_defaults(handler=command_cherrypy) 

    # html
    parser_html = subparsers.add_parser('html')
    parser_html.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_html.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_html.set_defaults(handler=command_html) 
 
    # alert
    parser_alert = subparsers.add_parser('alert')
    parser_alert.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_alert.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_alert.set_defaults(handler=command_alert) 

    # all
    parser_all = subparsers.add_parser('all')
    parser_all.add_argument('-c', '--conf', 
                             action='store', 
                             dest='conf', 
                             default='')
    parser_all.add_argument('-o', '--option', 
                             action='store', 
                             dest='option', 
                             default='')
    parser_all.set_defaults(handler=command_all) 

    args = parser.parse_args()

    if hasattr(args, 'handler'):
        args.handler(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
