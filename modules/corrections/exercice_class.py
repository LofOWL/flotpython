# -*- coding: utf-8 -*-

from __future__ import print_function

from IPython.display import HTML

from log import log_correction
from rendering import (Table, TableRow, TableCell, CellLegend,
                       font_style, header_font_style,
                       ok_style, ko_style,
                       center_cell_style, left_cell_style, right_cell_style
)


default_correction_columns = 30, 40, 40
default_exemple_columns = 40, 60

##########
class ScenarioClass(list):
    """
    Describes a scenario that can be applied to a class

    Typically we want to create an instance (using some args),
    and then run some methods (still with some args)

    So a class scenario in its simpler form is defined as a list
    of couples of the form 
    ( method_name, Args_object )
    the latter being an instance of ArgsKeywords or Args
    """

    def __init__(self):
        list.__init__(self)

    def set_init_args(self, args_obj):
        """
        Defines the arguments to constructor
        """
        if self and self[0][0] == '__init__':
            print("Only one __init__ step is allowed")
            return
        self.insert(0, ('__init__', args_obj))

    def add_step (self, methodname, args_obj):
        """
        Scenario is to proceed by calling method
        of that name with these arguments
        """
        self.append( (methodname, args_obj,) )

##########
class ExerciceClass(object):
    """
    Much like the ExerciceFunction class, this allows to define
    an exercice as
    (*) a solution which is the correct implementation of a class
    (*) a list of scenarios that will be executed on that class

    From that plus a few accessories for fine-grained customization
    we can generate online exemple and correction.
    """
    
    def __init__(self, solution, scenarios,
                 correction_columns=None, exemple_columns=None,
                 exemple_how_many=1,
                 copy_mode='deep',
                 layout=None,
                 obj_name='o'):
        self.solution = solution
        self.scenarios = scenarios
        self.name = solution.__name__
        self.correction_columns = correction_columns 
        self.exemple_columns = exemple_columns 
        self.exemple_how_many = exemple_how_many
        self.copy_mode = copy_mode
        # applicable to all cells whose Args instance has not specified a layout
        self.layout = layout
        self.obj_name = obj_name

    def correction (self, student_class):

        overall = True

        # should be customizable
        columns = self.correction_columns
        if not columns:
            columns = default_correction_columns
        c1, c2, c3 = columns
        ref_class = self.solution
        
        table = Table(style=font_style)
        html = table.header()

        for i, scenario in enumerate(self.scenarios):
            # first step has to be a constructor
            assert len(scenario)>=1 and scenario[0][0] == '__init__'
            
            methodname, args_obj = scenario[0]

            # start of scenario
            legend = CellLegend("Scénario {}".format(i+1))
            html += TableRow(cells=[TableCell(legend, colspan=4, tag='th',
                                              style='text-align:center')],
                             style=header_font_style).html()
            cells = [ TableCell(CellLegend(x), tag='th') for x in ('Appel', 'Attendu', 'Obtenu','')]
            html += TableRow(cells = cells).html()

            # XXX TODO : take care of copying Args instances before using them

            # initialize both objects
            try:
                # clone args for both usages
                ref_args = args_obj.clone(self.copy_mode)
                student_args = args_obj.clone(self.copy_mode)
                # always render the classname - with a name
                args_obj.render_function_name(self.name)
                args_obj.render_prefix("{}=".format(self.obj_name))
                # initialize both objects
                ref_obj = ref_args.init_obj(ref_class)
                student_obj = student_args.init_obj(student_class)
                cells = ( TableCell(args_obj, layout=self.layout, width=c1),
                          TableCell(CellLegend('-')),
                          TableCell(CellLegend('-')),
                          TableCell(CellLegend('OK')))
                html += TableRow(cells=cells, style=ok_style).html()
            except Exception as e:
                import traceback
                traceback.print_exc()
                cell1 = TableCell(args_obj, layout=self.layout, width=c1+c2, colspan=2)
                error = "Exception {}".format(e)
                cell2 = TableCell(CellLegend(error), width=c3)
                cell3 = TableCell(CellLegend('KO'))
                html += TableRow(cells=(cell1, cell2, cell3), style=ko_style).html()
                overall = False
                continue
            
            # other steps of that scenario
            for methodname, args_obj in scenario[1:]:
                # clone args for both usages
                ref_args = args_obj.clone(self.copy_mode)
                student_args = args_obj.clone(self.copy_mode)
                # so that we display the function name
                args_obj.render_function_name(methodname)
                args_obj.render_prefix("{}.".format(self.obj_name))
                ref_result = ref_args.call_obj(ref_obj, methodname)
                try:
                    student_result = student_args.call_obj(student_obj, methodname)
                    if ref_result == student_result:
                        style = ok_style
                        msg = 'OK'
                    else:
                        style = ko_style
                        msg = 'KO'
                        overall = False
                except Exception as e:
                    style = ko_style
                    msg = 'KO'
                    overall = False
                    student_result = "Exception {}".format(e)
                    
                # xxx styling maybe a little too much...
                cells = (TableCell(args_obj, style=right_cell_style, layout=self.layout, width=c1),
                         TableCell(ref_result, layout=self.layout, width=c2),
                         TableCell(student_result, layout=self.layout, width=c3),
                         TableCell(CellLegend(msg)))
                html += TableRow (cells=cells, style=style).html()

        log_correction(self.name, overall)

        html += "</table>"

        return HTML(html)

    def exemple(self):
        """
        display a table with example scenarios
        """
        how_many = self.exemple_how_many
        columns = self.exemple_columns if self.exemple_columns else default_exemple_columns
        c1, c2 = columns
        exo_layout = self.layout
        ref_class = self.solution

        how_many_samples = self.exemple_how_many if self.exemple_how_many \
                           else len(self.scenarios)

        table = Table(style=font_style)
        html = table.header()

        sample_scenarios = self.scenarios[:how_many_samples]
        for i, scenario in enumerate(sample_scenarios):
            # first step has to be a constructor
            assert len(scenario)>=1 and scenario[0][0] == '__init__'
            
            methodname, args_obj = scenario[0]
            # always render the classname
            args_obj.render_function_name(self.name)

            # start of scenario
            legend = CellLegend("Scénario {}".format(i+1))
            html += TableRow(
                cells=[TableCell(legend, colspan=4, tag='th',
                                 style='text-align:center')],
                style=header_font_style).html()
            cells = [ TableCell(CellLegend(x), tag='th') for x in ('Appel', 'Attendu')]
            html += TableRow(cells = cells).html()
            
            ref_args = args_obj.clone(self.copy_mode)
            ref_args.render_function_name(self.name)
            ref_obj = ref_args.init_obj(ref_class)
            cells = (TableCell(args_obj, layout=self.layout, width=c1),
                     TableCell(CellLegend('-')))
            html += TableRow(cells=cells).html()

            for methodname, args_obj in scenario[1:]:
                ref_args = args_obj.clone(self.copy_mode)
                ref_args.render_function_name(methodname)
                ref_result = ref_args.call_obj(ref_obj, methodname)
                cells = ( TableCell(ref_args, style=right_cell_style, layout=self.layout, width=c1),
                          TableCell(ref_result, layout=self.layout, width=c2))
                html += TableRow(cells=cells).html()

        html += table.footer()
        return HTML(html)
            
        
                                   