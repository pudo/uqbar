# Uqbar

An issue with NER is that it generates a large number of false positives. These include:

* Mis-detected parts of sentences
* Countries, places, etc. (mis-tagged as people or organisations)
* Government bodies that are not of interest to us.

## Generate candidate list

```sql
SELECT dt.text, dt.type, SUM(dt.weight) AS weight
    FROM document_tag dt
        LEFT JOIN document d ON d.id = dt.document_id
    WHERE origin IN ('spacy', 'polyglot')
    GROUP BY dt.text, dt.type
    ORDER BY SUM(dt.weight) DESC;
```