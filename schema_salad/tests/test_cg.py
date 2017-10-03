import cg_metaschema
import unittest
import logging
from util import get_data
import json
from matcher import JsonDiffMatcher
import os

class TestGeneratedMetaschema(unittest.TestCase):
    def test_load(self):
        doc = {
            "type": "record",
            "fields": [{
                "name": "hello",
                "doc": "Hello test case",
                "type": "string"
            }]
        }
        rs = cg_metaschema.RecordSchema(doc, "http://example.com/", cg_metaschema.LoadingOptions())
        self.assertEqual("record", rs.type)
        self.assertEqual("http://example.com/#hello", rs.fields[0].name)
        self.assertEqual("Hello test case", rs.fields[0].doc)
        self.assertEqual("string", rs.fields[0].type)
        self.assertEqual({
            "type": "record",
            "fields": [{
                "name": "http://example.com/#hello",
                "doc": "Hello test case",
                "type": "string"
            }]
        }, rs.save())

    def test_err(self):
        doc = {
            "doc": "Hello test case",
            "type": "string"
        }
        with self.assertRaises(cg_metaschema.ValidationException):
            rf = cg_metaschema.RecordField(doc, "", cg_metaschema.LoadingOptions())

    def test_include(self):
        doc = {
            "name": "hello",
            "doc": [{"$include": "hello.txt"}],
            "type": "documentation"
        }
        rf = cg_metaschema.Documentation(doc, "http://example.com/", cg_metaschema.LoadingOptions(fileuri="file://"+get_data("tests/_")))
        self.assertEqual("http://example.com/#hello", rf.name)
        self.assertEqual(["hello world!\n"], rf.doc)
        self.assertEqual("documentation", rf.type)
        self.assertEqual({
                "name": "http://example.com/#hello",
                "doc": ["hello world!\n"],
                "type": "documentation"
        }, rf.save())

    def test_import(self):
        doc = {
            "type": "record",
            "fields": [{
                "$import": "hellofield.yml"
            }]
        }
        lead = "file://"+os.path.normpath(get_data("tests"))
        rs = cg_metaschema.RecordSchema(doc, "http://example.com/", cg_metaschema.LoadingOptions(fileuri=lead+"/_"))
        self.assertEqual("record", rs.type)
        self.assertEqual(lead+"/hellofield.yml#hello", rs.fields[0].name)
        self.assertEqual("hello world!\n", rs.fields[0].doc)
        self.assertEqual("string", rs.fields[0].type)
        self.assertEqual({
            "type": "record",
            "fields": [{
                "name": lead+"/hellofield.yml#hello",
                "doc": "hello world!\n",
                "type": "string"
            }]
        }, rs.save())


    def test_import2(self):
        rs = cg_metaschema.load_document("file://"+get_data("tests/docimp/d1.yml"), "", cg_metaschema.LoadingOptions())
        self.assertEqual([{'doc': [u'*Hello*', 'hello 2', u'*dee dee dee five*',
                                   'hello 3', 'hello 4', u'*dee dee dee five*',
                                   'hello 5'],
                           'type': 'documentation',
                           'name': "file://"+get_data("tests/docimp/d1.yml#Semantic_Annotations_for_Linked_Avro_Data")+''}],
              [r.save() for r in rs])

    def test_err2(self):
        doc = {
            "type": "rucord",
            "fields": [{
                "name": "hello",
                "doc": "Hello test case",
                "type": "string"
            }]
        }
        with self.assertRaises(cg_metaschema.ValidationException):
            rs = cg_metaschema.RecordSchema(doc, "", cg_metaschema.LoadingOptions())

    def test_idmap(self):
        doc = {
            "type": "record",
            "fields": {
                "hello": {
                    "doc": "Hello test case",
                    "type": "string"
                }
            }
        }
        rs = cg_metaschema.RecordSchema(doc, "http://example.com/", cg_metaschema.LoadingOptions())
        self.assertEqual("record", rs.type)
        self.assertEqual("http://example.com/#hello", rs.fields[0].name)
        self.assertEqual("Hello test case", rs.fields[0].doc)
        self.assertEqual("string", rs.fields[0].type)
        self.assertEqual({
            "type": "record",
            "fields": [{
                "name": "http://example.com/#hello",
                "doc": "Hello test case",
                "type": "string"
            }]
        }, rs.save())

    def test_idmap2(self):
        doc = {
            "type": "record",
            "fields": {
                "hello": "string"
            }
        }
        rs = cg_metaschema.RecordSchema(doc, "http://example.com/", cg_metaschema.LoadingOptions())
        self.assertEqual("record", rs.type)
        self.assertEqual("http://example.com/#hello", rs.fields[0].name)
        self.assertEqual(None, rs.fields[0].doc)
        self.assertEqual("string", rs.fields[0].type)
        self.assertEqual({
            "type": "record",
            "fields": [{
                "name": "http://example.com/#hello",
                "type": "string"
            }]
        }, rs.save())

    def test_load_metaschema(self):
        doc = cg_metaschema.load_document("file://"+get_data("metaschema/metaschema.yml"), "", cg_metaschema.LoadingOptions())
        with open(get_data("tests/metaschema-pre.yml")) as f:
            pre = json.load(f)
        saved = [d.save() for d in doc]
        self.assertEqual(saved, JsonDiffMatcher(pre))

if __name__ == '__main__':
    unittest.main()
