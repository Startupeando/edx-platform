from django.conf import settings
from xml.dom.minidom import parse, parseString

from lxml import etree

from auth.models import UserProfile

''' This file will eventually form an abstraction layer between the
course XML file and the rest of the system. 

TODO: Shift everything from xml.dom.minidom to XPath (or XQuery)
'''

def item(l, default="", process=lambda x:x):
    if len(l)==0:
        return default
    elif len(l)==1:
        return process(l[0])
    else:
        raise Exception('Malformed XML')
    

def course_file(user):
    # TODO: Cache. Also, return the libxml2 object. 
    return settings.DATA_DIR+UserProfile.objects.get(user=user).courseware

def module_xml(coursefile, module, id_tag, module_id):
    ''' Get XML for a module based on module and module_id. Assumes
        module occurs once in courseware XML file.. '''
    doc = etree.parse(coursefile)

    # Sanitize input
    if not module.isalnum():
        raise Exception("Module is not alphanumeric")
    if not module_id.isalnum():
        raise Exception("Module ID is not alphanumeric")
    xpath_search='//*/{module}[(@{id_tag} = "{id}") or (@id = "{id}")]'.format(module=module, 
                                                           id_tag=id_tag,
                                                           id=module_id)
    #result_set=doc.xpathEval(xpath_search)
    result_set=doc.xpath(xpath_search)
    if len(result_set)>1:
        print "WARNING: Potentially malformed course file", module, module_id
    if len(result_set)==0:
        return None
    return etree.tostring(result_set[0])
    #return result_set[0].serialize()

def toc_from_xml(coursefile, active_chapter, active_section):
    dom=parse(coursefile)

    course = dom.getElementsByTagName('course')[0]
    name=course.getAttribute("name")
    chapters = course.getElementsByTagName('chapter')
    ch=list()
    for c in chapters:
        if c.getAttribute("name") == 'hidden':
            continue
        sections=list()
        for s in c.getElementsByTagName('section'):
            sections.append({'name':s.getAttribute("name"), 
                             'time':s.getAttribute("time"), 
                             'format':s.getAttribute("format"), 
                             'due':s.getAttribute("due"),
                             'active':(c.getAttribute("name")==active_chapter and \
                                           s.getAttribute("name")==active_section)})
        ch.append({'name':c.getAttribute("name"), 
                   'sections':sections,
                   'active':(c.getAttribute("name")==active_chapter)})
    return ch

def dom_select(dom, element_type, element_name):
    if dom==None:
        return None
    elements=dom.getElementsByTagName(element_type)
    for e in elements:
        if e.getAttribute("name")==element_name:
            return e
    return None

