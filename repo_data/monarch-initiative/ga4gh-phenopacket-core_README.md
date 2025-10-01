======================
GA4GH Phenopacket Core
======================

Python convenience wrappers for Phenopacket Schema.

Examples
^^^^^^^^

We recommend importing all classes using the star import:

.. code-block:: python

  >>> from ppsc.v202 import *

Create a Phenopacket Schema element
***********************************

The library simplifies creation of the Phenopacket Schema elements:


.. code-block:: python

  >>> subject = Individual(id='retinoblastoma', sex=Sex.FEMALE)

The objects can be modified in place:

.. code-block:: python

  >>> subject.sex = Sex.MALE
  >>> subject.sex.name
  'MALE'

including assignment of a more complex elements such as `TimeElement`:

.. code-block:: python

  >>> subject.time_at_last_encounter = TimeElement(element=Age(iso8601duration='P6M'))
  >>> subject.time_at_last_encounter
  TimeElement(element=Age(iso8601duration=P6M))

Serialize to/from JSON
**********************

Each schema element can be dumped into JSON using `JsonSerializer` with a similar semantics as Python `json` module:

.. code-block:: python

  >>> from ppsc.parse.json import JsonSerializer
  >>> serializer = JsonSerializer()

The serializer needs a text IO handle, such as one you'll get with `open('foo.json')`.
Here, however, we use `io.StringIO` instead:

.. code-block:: python

  >>> import io
  >>> fh = io.StringIO()

Now we can serialize a element to JSON:

.. code-block:: python

  >>> serializer.serialize(subject, fh)
  >>> fh.getvalue()
  '{"id": "retinoblastoma", "alternateIds": [], "timeAtLastEncounter": {"age": {"iso8601duration": "P6M"}}, "sex": "MALE"}'

We can use `JsonDeserializer` to deserialize the JSON string and get the same element back:

.. code-block:: python

  >>> from ppsc.parse.json import JsonDeserializer
  >>> deserializer = JsonDeserializer()
  >>> _ = fh.seek(0)  # rewind the buffer
  >>> other = deserializer.deserialize(fh, Individual)
  >>> subject == other
  True

Serialize to/from JSON
**********************

Similarly, we can dump/load any element to/from Protobuf bytes:

.. code-block:: python

  >>> byte_buf = io.BytesIO()
  >>> subject.time_at_last_encounter.dump_pb(byte_buf)
  >>> _ = byte_buf.seek(0)  # rewind
  >>> subject.time_at_last_encounter == TimeElement.from_pb(byte_buf)
  True


Documentation
^^^^^^^^^^^^^

Find more info in our detailed documentation:

- `Stable documentation <https://monarch-initiative.github.io/ga4gh-phenopacket-core/stable>`_: last release on the `main` branch
- `Latest documentation <https://monarch-initiative.github.io/ga4gh-phenopacket-core/latest>`_: bleeding edge, last commit on the `development` branch
