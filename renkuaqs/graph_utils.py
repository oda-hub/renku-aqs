import os
import typing
import pydotplus
import rdflib

from rdflib.tools.rdf2dot import LABEL_PROPERTIES
from lxml import etree
from dateutil import parser
from astropy.coordinates import SkyCoord, Angle


def customize_edge(edge: typing.Union[pydotplus.Edge]):
    if 'label' in edge.obj_dict['attributes']:
        edge_html = etree.fromstring(edge.obj_dict['attributes']['label'][1:-1])
        # simple color code
        # those two are not relevant at the moment since new predicates have been infered
        # if edge_html.text == 'oda:isRequestingAstroObject':
        #     edge.obj_dict['attributes']['color'] = '#2986CC'
        # if edge_html.text == 'oda:isUsing':
        #     edge.obj_dict['attributes']['color'] = '#53D06A'
        # TODO remove first part of the label ?
        edge_html.text = edge_html.text.split(":")[1]
        edge.set_label('< ' + etree.tostring(edge_html, encoding='unicode') + ' >')


def customize_node(node: typing.Union[pydotplus.Node],
                   type_label_values_dict=None
                   ):
    if 'label' in node.obj_dict['attributes']:
        # parse the whole node table into a lxml object
        table_html = etree.fromstring(node.get_label()[1:-1])
        tr_list = table_html.findall('tr')

        # modify the first row, hence the title of the node, and then all the rest
        id_node = None
        td_list_first_row = tr_list[0].findall('td')
        if td_list_first_row is not None:
            td_list_first_row[0].attrib.pop('bgcolor')
            b_element_title = td_list_first_row[0].findall('B')
            if b_element_title is not None and b_element_title[0].text in type_label_values_dict:
                id_node = b_element_title[0].text
            if id_node is not None:
                # change title of the node
                if type_label_values_dict[b_element_title[0].text] != 'CommandParameter':
                    b_element_title[0].text = type_label_values_dict[b_element_title[0].text]
                if b_element_title[0].text.startswith('CommandOutput') and \
                        b_element_title[0].text != 'CommandOutput':
                    b_element_title[0].text = b_element_title[0].text[13:]
                # apply styles (shapes, colors etc etc)
                table_html.attrib['border'] = '0'
                table_html.attrib['cellborder'] = '0'
                node.set_style("filled")
                node.set_shape("box")
                # color and shape change
                #1B81FB
                if type_label_values_dict[id_node] == 'Action':
                    node.set_shape("diamond")
                    node.set_color("#D5C15D")
                elif type_label_values_dict[id_node] == 'CommandOutput':
                    node.set_color("#FFFF00")
                elif type_label_values_dict[id_node] == 'CommandOutputImage' or \
                        type_label_values_dict[id_node] == 'CommandOutputFitsFile':
                    table_html.attrib['border'] = '1'
                    node.set_color("#FFFFFF")
                elif type_label_values_dict[id_node] == 'CommandOutputNotebook':
                    node.set_color("#DBA3BC")
                elif type_label_values_dict[id_node] == 'CommandInput':
                    node.set_color("#DBA3BC")
                elif type_label_values_dict[id_node] == 'CommandParameter':
                    node.set_color("#6262be")
                elif type_label_values_dict[id_node] == 'AstroqueryModule':
                    node.set_shape("ellipse")
                    node.set_color("#00CC00")
                elif type_label_values_dict[id_node] == 'AstrophysicalObject':
                    node.set_shape("ellipse")
                    node.set_color("#6262be")
                elif type_label_values_dict[id_node] == 'AstrophysicalRegion':
                    node.set_shape("ellipse")
                    node.set_color("#6262bf")
                elif type_label_values_dict[id_node] == 'AstrophysicalImage':
                    node.set_shape("ellipse")
                    node.set_color("#6262bg")
                elif type_label_values_dict[id_node] == 'Angle' or \
                        type_label_values_dict[id_node] == 'SkyCoordinates' or \
                        type_label_values_dict[id_node] == 'Coordinates' or \
                        type_label_values_dict[id_node] == 'Position' or \
                        type_label_values_dict[id_node] == 'Pixels':
                    node.set_color("#1B81FB")
                # remove top row for the cells Action and CommandInput
                if type_label_values_dict[id_node] == 'CommandInput' or \
                        type_label_values_dict[id_node] == 'Action':
                    table_html.remove(tr_list[0])
                # remove not needed long id information
                table_html.remove(tr_list[1])
                # remove not-needed information in the output tree nodes (eg defaultValue text, position value)
                for tr in tr_list:
                    list_td = tr.findall('td')
                    if len(list_td) == 2:
                        list_left_column_element = list_td[0].text.split(':')
                        # remove left side text (eg defaultValue)
                        tr.remove(list_td[0])
                        if 'align' in list_td[1].keys():
                            list_td[1].attrib['align'] = 'center'
                            list_td[1].attrib['colspan'] = '2'
                        # special case default_value table_row
                        if 'defaultValue' in list_left_column_element and \
                                type_label_values_dict[id_node] == 'CommandParameter':
                            list_args_commandParameter = list_td[1].text[1:-1].split(' ')
                            if b_element_title is not None and b_element_title[0].text in type_label_values_dict:
                                b_element_title[0].text = list_args_commandParameter[0]
                                list_td[1].text = '"' + ' '.join(list_args_commandParameter[1:]) + '"'
                        if 'startedAtTime' in list_left_column_element:
                            # TODO to improve and understand how to parse xsd:dateTime time
                            parsed_startedAt_time = parser.parse(list_td[1].text.replace('^^xsd:dateTime', '')[1:-1])
                            # create an additional row to attach at the bottom, so that time is always at the bottom
                            bottom_table_row = etree.Element('tr')
                            time_td = etree.Element('td')
                            time_td.attrib['align'] = 'center'
                            time_td.attrib['colspan'] = '2'
                            time_td.text = parsed_startedAt_time.strftime('%Y-%m-%d %H:%M:%S')
                            bottom_table_row.append(time_td)
                            tr.remove(list_td[1])
                            table_html.remove(tr)
                            table_html.append(bottom_table_row)

                        # remove trailing and leading double quotes
                        list_td[1].text = list_td[1].text[1:-1]
                        # bold text in case of action
                        if type_label_values_dict[id_node] == 'Action' and \
                                 'command' in list_left_column_element:
                            bold_text_element = etree.Element('B')
                            bold_text_element.text = list_td[1].text
                            list_td[1].append(bold_text_element)
                            list_td[1].text = ""
                        # italic ad bold in case of input
                        if type_label_values_dict[id_node] == 'CommandInput':
                            bold_text_element = etree.Element('B')
                            italic_text_element = etree.Element('I')
                            italic_text_element.text = list_td[1].text
                            bold_text_element.append(italic_text_element)
                            list_td[1].append(bold_text_element)
                            list_td[1].text = ""

            # serialize back the table html
            node.obj_dict['attributes']['label'] = '< ' + etree.tostring(table_html, encoding='unicode') + ' >'


def build_query_where(input_notebook: str = None):
    # TODO still to fully verify that the results is the expected one
    if input_notebook is not None:
        query_where = f"""WHERE {{
            {{
            ?action a <http://schema.org/Action> ; 
                <https://swissdatasciencecenter.github.io/renku-ontology#hasInputs> ?actionParamInput ;
                <https://swissdatasciencecenter.github.io/renku-ontology#command> ?actionCommand ;
                ?has ?actionParam .

            ?actionParamInput a ?actionParamInputType ;
                <http://schema.org/defaultValue> '{input_notebook}' .

            FILTER ( ?actionParamInputType = <https://swissdatasciencecenter.github.io/renku-ontology#CommandInput>) .

            FILTER (?has IN (<https://swissdatasciencecenter.github.io/renku-ontology#hasArguments>, 
                <https://swissdatasciencecenter.github.io/renku-ontology#hasOutputs>
                ))

            ?actionParam a ?actionParamType ;
                <http://schema.org/defaultValue> ?actionParamValue .

            FILTER ( ?actionParamType IN (<https://swissdatasciencecenter.github.io/renku-ontology#CommandOutput>,
                                        <https://swissdatasciencecenter.github.io/renku-ontology#CommandParameter>)
                                        ) .
        """
    else:
        query_where = """WHERE {
            {
                ?action a <http://schema.org/Action> ;
                    <https://swissdatasciencecenter.github.io/renku-ontology#command> ?actionCommand ;
                    ?has ?actionParam .

                FILTER (?has IN (<https://swissdatasciencecenter.github.io/renku-ontology#hasArguments>,
                    <https://swissdatasciencecenter.github.io/renku-ontology#hasOutputs>,
                    <https://swissdatasciencecenter.github.io/renku-ontology#hasInputs>
                    ))

                ?actionParam a ?actionParamType ;
                    <http://schema.org/defaultValue> ?actionParamValue .

                FILTER ( ?actionParamType IN (<https://swissdatasciencecenter.github.io/renku-ontology#CommandOutput>,
                                        <https://swissdatasciencecenter.github.io/renku-ontology#CommandParameter>,
                                        <https://swissdatasciencecenter.github.io/renku-ontology#CommandInput>)
                                        ) .
        """

    query_where = query_where + """
                OPTIONAL { ?actionParam <https://swissdatasciencecenter.github.io/renku-ontology#position> ?actionPosition } .
            }

            {
                ?activity a ?activityType ;
                    <http://www.w3.org/ns/prov#startedAtTime> ?activityTime ;
                    <https://swissdatasciencecenter.github.io/renku-ontology#parameter> ?parameter_value ;
                    <http://www.w3.org/ns/prov#qualifiedAssociation> ?activity_qualified_association .

                ?activity_qualified_association <http://www.w3.org/ns/prov#hadPlan> ?action .

                {
                    ?run <http://odahub.io/ontology#isUsing> ?aq_module ;
                         <http://odahub.io/ontology#isRequestingAstroObject> ?a_object ;
                         a ?run_rdf_type ;
                         ^oa:hasBody/oa:hasTarget ?runId ;
                         ^oa:hasBody/oa:hasTarget ?activity .

                    ?aq_module <http://purl.org/dc/terms/title> ?aq_module_name ;
                        a ?aq_mod_rdf_type .

                    ?a_object <http://purl.org/dc/terms/title> ?a_object_name ;
                        a ?a_obj_rdf_type .

                    OPTIONAL {{ ?run <http://purl.org/dc/terms/title> ?run_title . }}

                    ?run ?p ?o .

                    FILTER (!CONTAINS(str(?a_object), " ")) .
                }
                UNION
                {
                    ?run <http://odahub.io/ontology#isUsing> ?aq_module ;
                         <http://odahub.io/ontology#isRequestingAstroRegion> ?a_region ;
                         a ?run_rdf_type ;
                         ^oa:hasBody/oa:hasTarget ?runId ;
                         ^oa:hasBody/oa:hasTarget ?activity .

                    ?aq_module a ?aq_mod_rdf_type ;
                        <http://purl.org/dc/terms/title> ?aq_module_name .

                    ?a_region a ?a_region_type ; 
                        <http://purl.org/dc/terms/title> ?a_region_name ;
                        <http://odahub.io/ontology#isUsingSkyCoordinates> ?a_sky_coordinates ;
                        <http://odahub.io/ontology#isUsingRadius> ?a_radius .

                    ?a_sky_coordinates a ?a_sky_coordinates_type ;
                        <http://purl.org/dc/terms/title> ?a_sky_coordinates_name .

                    ?a_radius a ?a_radius_type ;
                        <http://purl.org/dc/terms/title> ?a_radius_name .

                    OPTIONAL {{ ?run <http://purl.org/dc/terms/title> ?run_title . }}

                    ?run ?p ?o .
                }
                UNION
                {
                    ?run <http://odahub.io/ontology#isUsing> ?aq_module ;
                         <http://odahub.io/ontology#isRequestingAstroImage> ?a_image ;
                         a ?run_rdf_type ;
                         ^oa:hasBody/oa:hasTarget ?runId ;
                         ^oa:hasBody/oa:hasTarget ?activity .

                    ?aq_module a ?aq_mod_rdf_type ;
                        <http://purl.org/dc/terms/title> ?aq_module_name .

                    ?a_image a ?a_image_type ;
                        <http://purl.org/dc/terms/title> ?a_image_name ;

                    OPTIONAL {{ ?a_image <http://odahub.io/ontology#isUsingCoordinates> ?a_coordinates .
                         ?a_coordinates a ?a_coordinates_type ;
                             <http://purl.org/dc/terms/title> ?a_coordinates_name .
                    }}
                    OPTIONAL {{ ?a_image <http://odahub.io/ontology#isUsingPosition> ?a_position .
                         ?a_position a ?a_position_type ;
                             <http://purl.org/dc/terms/title> ?a_position_name .
                    }}
                    OPTIONAL {{ ?a_image <http://odahub.io/ontology#isUsingRadius> ?a_radius .
                        ?a_radius a ?a_radius_type ;
                            <http://purl.org/dc/terms/title> ?a_radius_name .
                    }}
                    OPTIONAL {{ ?a_image <http://odahub.io/ontology#isUsingPixels> ?a_pixels .
                        ?a_pixels a ?a_pixels_type ;
                            <http://purl.org/dc/terms/title> ?a_pixels_name .
                    }}
                    OPTIONAL {{ ?a_image <http://odahub.io/ontology#isUsingImageBand> ?a_image_band .
                        ?a_image_band a ?a_image_band_type ;
                            <http://purl.org/dc/terms/title> ?a_image_band_name .
                    }}

                    OPTIONAL {{ ?run <http://purl.org/dc/terms/title> ?run_title . }}

                    ?run ?p ?o .
                }
            }
        }
        """
    return query_where


def build_query_construct(input_notebook: str = None, no_oda_info=False):
    if input_notebook is not None:
        query_construct_action = f"""
                ?action a <http://schema.org/Action> ;
                    <https://swissdatasciencecenter.github.io/renku-ontology#command> ?actionCommand ;
                    <https://swissdatasciencecenter.github.io/renku-ontology#hasInputs> ?actionParamInput ;
                    ?has ?actionParam .

                ?actionParamInput a ?actionParamInputType ;
                    <http://schema.org/defaultValue> '{input_notebook}' .

                ?actionParam a ?actionParamType ;
                    <https://swissdatasciencecenter.github.io/renku-ontology#position> ?actionPosition ;
                    <http://schema.org/defaultValue> ?actionParamValue .
        """
    else:
        query_construct_action = """
                ?action a <http://schema.org/Action> ;
                    <https://swissdatasciencecenter.github.io/renku-ontology#command> ?actionCommand ;
                    ?has ?actionParam .

                ?actionParam a ?actionParamType ;
                    <https://swissdatasciencecenter.github.io/renku-ontology#position> ?actionPosition ;
                    <http://schema.org/defaultValue> ?actionParamValue .
        """
    # add time activity information
    query_construct_action += """
            ?activity a ?activityType ;
                <http://www.w3.org/ns/prov#startedAtTime> ?activityTime ;
                <http://www.w3.org/ns/prov#qualifiedAssociation> ?activity_qualified_association .

            ?activity_qualified_association <http://www.w3.org/ns/prov#hadPlan> ?action .
    """

    query_construct_oda_info = ""
    if not no_oda_info:
        query_construct_oda_info += """
                ?run <http://odahub.io/ontology#isRequestingAstroObject> ?a_object ;
                    <http://odahub.io/ontology#isRequestingAstroRegion> ?a_region ;
                    <http://odahub.io/ontology#isRequestingAstroImage> ?a_image ;
                    <http://purl.org/dc/terms/title> ?run_title ;
                    <http://odahub.io/ontology#isUsing> ?aq_module ;
                    oa:hasTarget ?activity ;
                    a ?run_rdf_type .

                ?aq_module <https://odahub.io/ontology#AQModule> ?aq_module_name ;
                    a ?aq_mod_rdf_type .

                ?a_object <https://odahub.io/ontology#AstroObject> ?a_object_name ;
                    a ?a_obj_rdf_type .

                ?a_region a ?a_region_type ; 
                    <http://purl.org/dc/terms/title> ?a_region_name ;
                    <http://odahub.io/ontology#isUsingSkyCoordinates> ?a_sky_coordinates ;
                    <http://odahub.io/ontology#isUsingRadius> ?a_radius .

                ?a_image a ?a_image_type ;
                    <http://purl.org/dc/terms/title> ?a_image_name ;
                    <http://odahub.io/ontology#isUsingCoordinates> ?a_coordinates ;
                    <http://odahub.io/ontology#isUsingPosition> ?a_position ;
                    <http://odahub.io/ontology#isUsingRadius> ?a_radius ;
                    <http://odahub.io/ontology#isUsingPixels> ?a_pixels ;
                    <http://odahub.io/ontology#isUsingImageBand> ?a_image_band .

                ?a_pixels a ?a_pixels_type ;
                    <http://purl.org/dc/terms/title> ?a_pixels_name .

                ?a_image_band a ?a_image_band_type ;
                    <http://purl.org/dc/terms/title> ?a_image_band_name .

                ?a_coordinates a ?a_coordinates_type ;
                    <http://purl.org/dc/terms/title> ?a_coordinates_name .
                    
                ?a_sky_coordinates a ?a_sky_coordinates_type ;
                    <http://purl.org/dc/terms/title> ?a_sky_coordinates_name .
                    
                ?a_position a ?a_position_type ;
                    <http://purl.org/dc/terms/title> ?a_position_name .

                ?a_radius a ?a_radius_type ;
                    <http://purl.org/dc/terms/title> ?a_radius_name .
            """

    query_construct = f"""CONSTRUCT {{
                {query_construct_action}
                {query_construct_oda_info}
            }}"""

    return query_construct


def clean_graph(g):
    # remove not-needed triples
    g.remove((None, rdflib.URIRef('http://www.w3.org/ns/prov#hadPlan'), None))
    g.remove((None, rdflib.URIRef('http://purl.org/dc/terms/title'), None))
    g.remove((None, rdflib.URIRef('http://www.w3.org/ns/prov#qualifiedAssociation'), None))
    g.remove((None, rdflib.URIRef('http://www.w3.org/ns/oa#hasTarget'), None))
    g.remove((None, rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#position'), None))
    g.remove((None, rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#hasArguments'), None))
    g.remove((None, rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#hasInputs'), None))
    # remove all the type triples
    g.remove((None, rdflib.RDF.type, None))


def analyze_types(g, type_label_values_dict):
    # analyze types
    types_list = g[:rdflib.RDF.type]
    for s, o in types_list:
        o_qname = g.compute_qname(o)
        s_label = label(s, g)
        type_label_values_dict[s_label] = o_qname[2]
    print("type_label_values_dict: ", type_label_values_dict)

def analyze_outputs(g, out_default_value_dict):
    # analyze outputs
    outputs_list = g[:rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#hasOutputs')]
    for s, o in outputs_list:
        s_label = label(s, g)
        if s_label not in out_default_value_dict:
            out_default_value_dict[s_label] = []
        output_obj_list = list(g[o:rdflib.URIRef('http://schema.org/defaultValue')])
        if len(output_obj_list) == 1:
            # get file extension
            file_extension = os.path.splitext(output_obj_list[0])[1][1:]

            if file_extension is not None:
                if file_extension in ['jpeg', 'jpg', 'png', 'gif', 'bmp']:
                    # removing old type, and assigning a new specific one
                    g.remove((o, rdflib.RDF.type, None))
                    g.add((o,
                           rdflib.RDF.type,
                           rdflib.URIRef("https://swissdatasciencecenter.github.io/renku-ontology#CommandOutputImage")))
                if file_extension in ['fits']:
                    # removing old type, and assigning a new specific one
                    g.remove((o, rdflib.RDF.type, None))
                    g.add((o,
                           rdflib.RDF.type,
                           rdflib.URIRef("https://swissdatasciencecenter.github.io/renku-ontology#CommandOutputFitsFile")))
                else:
                    if file_extension == 'ipynb':
                        g.remove((o, rdflib.RDF.type, None))
                        g.add((o,
                               rdflib.RDF.type,
                               rdflib.URIRef(
                                   "https://swissdatasciencecenter.github.io/renku-ontology#CommandOutputNotebook")))

            out_default_value_dict[s_label].append(output_obj_list[0])


def analyze_arguments(g, action_node_dict, args_default_value_dict):
    # analyze arguments (and join them all together)
    args_list = g[:rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#hasArguments')]
    for s, o in args_list:
        s_label = label(s, g)
        if s_label not in action_node_dict:
            action_node_dict[s_label] = s
        if s_label not in args_default_value_dict:
            args_default_value_dict[s_label] = []
        arg_obj_list = g[o:rdflib.URIRef('http://schema.org/defaultValue')]
        for arg_o in arg_obj_list:
            position_o = list(g[o:rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#position')])
            if len(position_o) == 1:
                args_default_value_dict[s_label].append((arg_o.n3().strip('\"'), position_o[0].value))
                g.remove((o, rdflib.URIRef('http://schema.org/defaultValue'), arg_o))
    # infer isArgumentOf property for each action, this implies the creation of the new CommandParameter nodes
    # with the related defaultValue
    for action in args_default_value_dict.keys():
        arg_pos_list = args_default_value_dict[action].copy()
        # order according their position
        arg_pos_list.sort(key=lambda arg_tuple: arg_tuple[1])
        iter_arg_pos_list = iter(arg_pos_list)
        for x, y in zip(iter_arg_pos_list, iter_arg_pos_list):
            # create the node
            # TODO id needs to be properly assigned! now the name of the parameter is used
            node_args = rdflib.URIRef("https://github.com/plans/84d9b437-4a55-4573-9aa3-4669ff641f1b/parameters/"
                                      + x[0].replace(" ", "_") + "_" + y[0].replace(" ", "_"))
            # link it to the action node
            g.add((node_args,
                   rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#isArgumentOf'),
                   action_node_dict[action]))
            # value for the node args
            g.add((node_args,
                   rdflib.URIRef('http://schema.org/defaultValue'),
                   rdflib.Literal((x[0] + " " + y[0]).strip())))
            # type for the node args
            # TODO to discuss what the best approach to assign the type case is:
            # to create a node with a dedicated type inferred from the arguments
            # G.add((node_args,
            #        rdflib.RDF.type,
            #        rdflib.URIRef("https://swissdatasciencecenter.github.io/renku-ontology#" + x[0])))
            # or still create a new CommandParameter and use the defaultValue information
            g.add((node_args,
                   rdflib.RDF.type,
                   rdflib.URIRef("https://swissdatasciencecenter.github.io/renku-ontology#CommandParameter")))


def label(x, g):
    for labelProp in LABEL_PROPERTIES:
        l = g.value(x, labelProp)
        if l:
            return l
    try:
        return g.namespace_manager.compute_qname(x)[2]
    except:
        return x


def analyze_inputs(g, in_default_value_dict):
    # analyze inputs
    inputs_list = g[:rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#hasInputs')]
    for s, o in inputs_list:
        s_label = label(s, g)
        if s_label not in in_default_value_dict:
            in_default_value_dict[s_label] = []
        input_obj_list = g[o]
        for input_p, input_o in input_obj_list:
            if input_p.n3() == "<http://schema.org/defaultValue>":
                in_default_value_dict[s_label].append(input_o.n3().strip('\"'))
        # infer isInputOf property
        g.add((o, rdflib.URIRef('https://swissdatasciencecenter.github.io/renku-ontology#isInputOf'), s))


def extract_activity_start_time(g):
    # extract the info about the activity start time
    # get the activities and extract for each the startedTime into, and attach it to the related Action
    start_time_activity_list = g[:rdflib.URIRef('http://www.w3.org/ns/prov#startedAtTime')]
    for activity_node, activity_start_time in start_time_activity_list:
        # get the association and then the action
        qualified_association_list = g[activity_node:rdflib.URIRef(
            'http://www.w3.org/ns/prov#qualifiedAssociation')]
        for association_node in qualified_association_list:
            plan_list = g[association_node:rdflib.URIRef('http://www.w3.org/ns/prov#hadPlan')]
            for plan_node in plan_list:
                g.add(
                    (plan_node, rdflib.URIRef('http://www.w3.org/ns/prov#startedAtTime'), activity_start_time))
                g.remove((activity_node, rdflib.URIRef('http://www.w3.org/ns/prov#startedAtTime'),
                          activity_start_time))


def process_oda_info(g):
    # find a way to the action form the Run by extracting activity qualified association
    run_target_list = g[:rdflib.URIRef('http://www.w3.org/ns/oa#hasTarget')]
    for run_node, activity_node in run_target_list:
        # run_node is the run, act_node is the activity
        qualified_association_list = g[activity_node:rdflib.URIRef('http://www.w3.org/ns/prov#qualifiedAssociation')]
        for association_node in qualified_association_list:
            action_list = g[association_node:rdflib.URIRef('http://www.w3.org/ns/prov#hadPlan')]
            # or plan_node list
            for action_node in action_list:
                # we inferred a connection from the run to an action
                # and we can now infer the request of a certain astroObject and the usage of a certain module
                used_module_list = list(g[run_node:rdflib.URIRef('http://odahub.io/ontology#isUsing')])
                # one module in use per annotation and one requested AstroObject/AstroRegion
                module_node = used_module_list[0]
                # query_object
                process_query_object_info(g, run_node=run_node, module_node=module_node, action_node=action_node)
                # query_region
                process_query_region_info(g, run_node=run_node, module_node=module_node, action_node=action_node)
                # get_images
                process_get_images_info(g, run_node=run_node, module_node=module_node, action_node=action_node)

                # some clean-up
                g.remove((run_node,
                          rdflib.URIRef('http://odahub.io/ontology#isUsing'),
                          None))
                g.remove((run_node,
                          rdflib.URIRef('http://odahub.io/ontology#isRequestingAstroRegion'),
                          None))
                g.remove((run_node,
                          rdflib.URIRef('http://odahub.io/ontology#isRequestingAstroObject'),
                          None))
                g.remove((run_node,
                          rdflib.URIRef('http://odahub.io/ontology#isRequestingAstroImage'),
                          None))


def process_query_object_info(g, run_node=None, module_node=None, action_node=None):
    requested_astroObject_list = list(
        g[run_node:rdflib.URIRef('http://odahub.io/ontology#isRequestingAstroObject')])
    if len(requested_astroObject_list) > 0:
        # if run_node is of the type query_object
        # for module_node in used_module_list:
        g.add((module_node, rdflib.URIRef('http://odahub.io/ontology#isUsedDuring'),
               action_node))
        # for astroObject_node in requested_astroObject_list:
        astroObject_node = requested_astroObject_list[0]
        g.add((module_node, rdflib.URIRef('http://odahub.io/ontology#requestsAstroObject'),
               astroObject_node))


def process_query_region_info(g, run_node=None, module_node=None, action_node=None):
    requested_astroRegion_list = list(
        g[run_node:rdflib.URIRef('http://odahub.io/ontology#isRequestingAstroRegion')])
    if len(requested_astroRegion_list) > 0:
        # if run_node is of the type query_region
        # for module_node in used_module_list:
        g.add((module_node, rdflib.URIRef('http://odahub.io/ontology#isUsedDuring'),
               action_node))
        # for astroObject_node in requested_astroObject_list:
        astroRegion_node = requested_astroRegion_list[0]
        g.add((module_node, rdflib.URIRef('http://odahub.io/ontology#requestsAstroRegion'),
               astroRegion_node))
        # sky coordinates info (if found, perhaps some for old query_region none was stored)
        sky_coordinates_list = list(
            g[astroRegion_node:rdflib.URIRef('http://odahub.io/ontology#isUsingSkyCoordinates')])
        if len(sky_coordinates_list) == 1:
            sky_coordinates_node = sky_coordinates_list[0]
            sky_coordinates_node_title = list(
                g[sky_coordinates_node:rdflib.URIRef('http://purl.org/dc/terms/title')])
            if len(sky_coordinates_node_title) == 1:
                # define an astropy SkyCoord object
                coords = sky_coordinates_node_title[0].value.split(" ")
                sky_coord_obj = SkyCoord(coords[0], coords[1], unit='degree')
                sky_coord_obj_default_value = 'RA=' + str(sky_coord_obj.ra.deg) + ' deg ' +\
                                              ' Dec=' + str(sky_coord_obj.dec.deg) + ' deg'
                g.add((sky_coordinates_node, rdflib.URIRef('http://schema.org/defaultValue'),
                       rdflib.Literal(sky_coord_obj_default_value)))
        # radius info (if found, perhaps some for old query_region none was stored)
        radius_list = list(
            g[astroRegion_node:rdflib.URIRef('http://odahub.io/ontology#isUsingRadius')])
        if len(radius_list) == 1:
            radius_node = radius_list[0]
            radius_node_title = list(
                g[radius_node:rdflib.URIRef('http://purl.org/dc/terms/title')])
            if len(radius_node_title) == 1:
                # define an astropy Angle object
                radius_obj = Angle(radius_node_title[0].value)
                radius_obj_default_value = str(radius_obj.arcmin) + " arcmin"
                g.add((radius_node, rdflib.URIRef('http://schema.org/defaultValue'),
                       rdflib.Literal(radius_obj_default_value)))


def process_get_images_info(g, run_node=None, module_node=None, action_node=None):
    requested_astroImage_list = list(
        g[run_node:rdflib.URIRef('http://odahub.io/ontology#isRequestingAstroImage')])
    if len(requested_astroImage_list) > 0:
        # if run_node is of the type get_images
        # for module_node in used_module_list:
        g.add((module_node, rdflib.URIRef('http://odahub.io/ontology#isUsedDuring'),
               action_node))
        # for astroObject_node in requested_astroObject_list:
        astroImage_node = requested_astroImage_list[0]
        g.add((module_node, rdflib.URIRef('http://odahub.io/ontology#requestsAstroImage'),
               astroImage_node))
        # position info (if found, they could be parsed top SkyCoordinates like in query_region)
        coordinates_list = list(
            g[astroImage_node:rdflib.URIRef('http://odahub.io/ontology#isUsingCoordinates')])
        if len(coordinates_list) == 1:
            coordinates_node = coordinates_list[0]
            coordinates_node_title = list(
                g[coordinates_node:rdflib.URIRef('http://purl.org/dc/terms/title')])
            if len(coordinates_node_title) == 1:
                coordinates = coordinates_node_title[0].value.split(" ")
                if len(coordinates) == 1:
                    coordinates_obj_default_value = ",".join(coordinates)
                    g.add((coordinates_node, rdflib.URIRef('http://schema.org/defaultValue'),
                           rdflib.Literal(coordinates_obj_default_value)))
        # position info (if found, they could be parsed top SkyCoordinates like in query_region)
        position_list = list(
            g[astroImage_node:rdflib.URIRef('http://odahub.io/ontology#isUsingPosition')])
        if len(position_list) == 1:
            sky_coordinates_node = position_list[0]
            sky_coordinates_node_title = list(
                g[sky_coordinates_node:rdflib.URIRef('http://purl.org/dc/terms/title')])
            if len(sky_coordinates_node_title) == 1:
                # define an astropy SkyCoord object
                coords = sky_coordinates_node_title[0].value.split(" ")
                if len(coords) == 2:
                    sky_coord_obj = SkyCoord(coords[0], coords[1], unit='degree')
                    sky_coord_obj_default_value = str(sky_coord_obj.dec.deg) + " " + str(
                        sky_coord_obj.ra.deg) + " unit=deg"
                else:
                    sky_coord_obj_default_value = ",".join(coords)
                g.add((sky_coordinates_node, rdflib.URIRef('http://schema.org/defaultValue'),
                       rdflib.Literal(sky_coord_obj_default_value)))
        # radius info (if found, perhaps some for old query_region none was stored)
        radius_list = list(
            g[astroImage_node:rdflib.URIRef('http://odahub.io/ontology#isUsingRadius')])
        if len(radius_list) == 1:
            radius_node = radius_list[0]
            radius_node_title = list(
                g[radius_node:rdflib.URIRef('http://purl.org/dc/terms/title')])
            if len(radius_node_title) == 1:
                # define an astropy Angle object
                radius_obj = Angle(radius_node_title[0].value)
                radius_obj_default_value = str(radius_obj.arcmin) + " unit=arcmin"
                g.add((radius_node, rdflib.URIRef('http://schema.org/defaultValue'),
                       rdflib.Literal(radius_obj_default_value)))
        # pixels info (if found, perhaps some for old query_region none was stored)
        pixels_list = list(
            g[astroImage_node:rdflib.URIRef('http://odahub.io/ontology#isUsingPixels')])
        if len(pixels_list) == 1:
            pixels_node = pixels_list[0]
            pixels_node_node_title = list(
                g[pixels_node:rdflib.URIRef('http://purl.org/dc/terms/title')])
            if len(pixels_node_node_title) == 1:
                # define an astropy SkyCoord object
                pixels = pixels_node_node_title[0].value.split(" ")
                pixels_obj_default_value = ",".join(pixels)
                g.add((pixels_node, rdflib.URIRef('http://schema.org/defaultValue'),
                       rdflib.Literal(pixels_obj_default_value)))
        # image band info (if found, perhaps some for old query_region none was stored)
        image_band_list = list(
            g[astroImage_node:rdflib.URIRef('http://odahub.io/ontology#isUsingImageBand')])
        if len(image_band_list) == 1:
            image_band_node = image_band_list[0]
            image_band_node_title = list(
                g[image_band_node:rdflib.URIRef('http://purl.org/dc/terms/title')])
            if len(image_band_node_title) == 1:
                # define an astropy SkyCoord object
                image_band_value = image_band_node_title[0].value
                g.add((image_band_node, rdflib.URIRef('http://schema.org/defaultValue'),
                       rdflib.Literal(image_band_value)))
