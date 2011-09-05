#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2011 Adriano Monteiro Marques
#
# Author:  Paul Pei <paul.kdash@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import pygtk
pygtk.require('2.0')
import gtk, gobject

from pygtk_chart.line_chart import LineChart, Graph

from higwidgets.higboxes import HIGVBox
from higwidgets.higwindows import HIGWindow

from umit.icm.agent.I18N import _
from umit.icm.agent.Application import theApp

class MenuBox(HIGVBox):

    def __init__(self, viewName):
        super(MenuBox, self).__init__()

        self.set_size_request(180, 180)

        self.treestore = gtk.TreeStore(str)

        piter = self.treestore.append(None, ['Total Reports'])

        self.treestore.append(piter, ['Report in Queue'])
        self.treestore.append(piter, ['Report generated'])
        self.treestore.append(piter, ['Report received'])
        piter = self.treestore.append(None, ['Task'])
        piter = self.treestore.append(None, ['Link'])
        self.treestore.append(piter, ['Linked super peer'])
        self.treestore.append(piter, ['Linked desktop agent'])
        self.treestore.append(piter, ['Linked mobile agent'])
        piter = self.treestore.append(None, ['Failed Times'])
        self.treestore.append(piter, ['super peer'])
        self.treestore.append(piter, ['desktop agent'])
        self.treestore.append(piter, ['mobile agent'])

        self.treeview = gtk.TreeView(self.treestore)
        self.tvcolumn = gtk.TreeViewColumn(viewName)
        self.treeview.append_column(self.tvcolumn)
        self.treeview.set_show_expanders(True)
        self.cell = gtk.CellRendererText()
        self.tvcolumn.pack_start(self.cell, True)
        self.tvcolumn.add_attribute(self.cell, 'text', 0)
        self.treeview.set_search_column(0)
        self.tvcolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        self.add(self.treeview)
        self.show_all()

class DashboardWindow(HIGWindow):

    def insert_text(self, buffer):
        iter = buffer.get_iter_at_offset(0)
        buffer.insert(iter,
                      "this is the test\n"
                      "we can place here\n"
                      "data about the softwre\n"
                      "correspondent with the chart above\n"
                      )

    def create_text(self):
        view = gtk.TextView()
        buffer = view.get_buffer()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.add(view)
        self.insert_text(buffer)
        scrolled_window.show_all()
        return scrolled_window

    def __create_widgets(self):
        chart = LineChart()
        graph = Graph("NewGraph", "Title", [(1,1),(2,2),(3,3)])
        chart.set_xrange((0, 10))
        chart.set_yrange((0, 5))
        chart.add_graph(graph)
        return chart

    def __pack_widgets(self):
        pass

    def create_chart(self):
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        chart=self.__create_widgets()
        scrolled_window.add(chart)
        scrolled_window.set_size_request(460,320)
        self.__pack_widgets()
        return scrolled_window

    def __create_reportdata(self):
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_size_request(450, 180)

        self.liststore = gtk.ListStore(str, str, str)
        self.treeview = gtk.TreeView(self.liststore)

        self.catacolumn = gtk.TreeViewColumn('Catagories')
        self.timescolumn = gtk.TreeViewColumn('Times')

        self.liststore.append(['Report sent to Aggregator',None, '45'])
        self.liststore.append(['Report sent to Super Agent', None, '50'])
        self.liststore.append(['Report sent to Desk Agent', None, '35'])

        self.treeview.append_column(self.catacolumn)
        self.treeview.append_column(self.timescolumn)

        self.catacell = gtk.CellRendererText()
        self.timecell = gtk.CellRendererText()

        self.catacolumn.pack_start(self.catacell, True)
        self.timescolumn.pack_start(self.timecell, True)

        self.catacolumn.set_attributes(self.catacell, text=0)
        self.timescolumn.set_attributes(self.timecell, text=2)
        self.treeview.set_search_column(0)
        self.catacolumn.set_sort_column_id(0)
        self.treeview.set_reorderable(True)
        scrolled_window.add(self.treeview)
        return scrolled_window

    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title(_('Dashboard'))
        #self.connect("delete_event", self.destroy)
        self.set_border_width(10)
        self.set_size_request(640, 500)

        hpaned = gtk.HPaned()
        self.add(hpaned)
        hpaned.show()

        tvexample = MenuBox(_('Dashboard Menu'))
        hpaned.add1(tvexample)

        vpaned = gtk.VPaned()
        hpaned.add2(vpaned)
        vpaned.show()

        board = self.create_chart()
        vpaned.add1(board)

        reportdata = self.__create_reportdata()
        vpaned.add2(reportdata)
        self.show()


if __name__ == "__main__":
    wnd = DashboardWindow()
    wnd.show_all()
    gtk.main()

