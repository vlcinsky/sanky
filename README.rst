==============================================================
Sanky - Flexible, reusable and concise configuration for Swarm
==============================================================
WARNING: Project is currently in VERY EXPERIMENTAL state.

Motivation
==========

-  You run one or more docker swarm stacks.
-  Trying to follow 12-factor application concepts, your stacks are
   configurable by means of environmental variables or swarm config
   and/or secret files.
-  Reading your ``docker-compose.yml``, ``.env``, config and secret
   files you realize that:

   -  some service definitions are repeating the same pattern, but
      options to define it and then reuse are very limited
   -  some parts of configuration in ``.env``, swarm config and/or
      secret files are repeating the same information
   -  there is no way to share configuration parameter across multiple
      stacks

-  the conclusion is simple: **There must be a better way!!!**

Quick Demo
==========

Note: this demo assumes ``sanka`` and all relevant tools are already
installed.

.. code:: shell

   $ git clone <config-repository> myclusters
   $ cd myclusters
   $ ls
   environments jsonnetfile.json jsonnetfile.lock.json lib vendor
   $ cd environments/myapp/prod
   $ ls
   main.jsonnet spec.json
   $ cat main.jsonnet
   (import 'myapp-publicsite/lib.libsonnet') +
   (import 'myapp-privatesite/lib.libsonnet') +
   {
     _config+:: {
       'myapp-publicsite'+: {
         home_title: 'Welcome Home',
         promo_actions+: {
           apples+: {
             reduction: '45%',
           },
         },
       },
     },
     _images+:: {
       myapp-privatesite+: {
         web: 'myapp/privatesite/web:v1.0',
       },
     },
   }

You may quickly deploy the site, but first, try to generate and explore
the ``docker-compose.yml`` files you are so familiar with:

.. code:: shell

   $ sk generate
   _deploy/myapp-publicsite/docker-compose.yml
   _deploy/myapp-privatesite/docker-compose.yml
   _deploy/myapp-privatesite/configs/web.ini
   _deploy/myapp-privatesite/secrets/users.auth

Warning: You are not supposed to edit these generated files manually,
only changes via ``main.jsonnet`` are applied.

To deploy, run (not implemented yet):

.. code:: shell

   sk apply

Update reduction value to "30%" and image version of web image into the
latest one you have just developed:

.. code:: shell

   $ cat main.jsonnet
   (import 'myapp-publicsite/lib.libsonnet') +
   (import 'myapp-privatesite/lib.libsonnet') +
   {
     _config+:: {
       'myapp-publicsite'+: {
         home_title: 'Welcome Home',
         promo_actions+: {
           apples+: {
             reduction: '30%',
           },
         },
       },
     },
     _images+:: {
       myapp-privatesite+: {
         web: 'myapp/privatesite/web:v1.1',
       },
     },
   }

and apply it (not implemented yet):

.. code:: shell

   sk apply

Scope and Requirements
======================

Scope
-----

Focus on generating parametrized configuration for set of swarm stacks.

Do not try to replace ``docker`` tooling.

Anyway, simplify it where appropriate, e.g.:

-  automatic ``docker stack deploy`` and ``docker stack rm`` for each
   stack in MuStack.
-  consider simplified management of single stack, when present in it's
   directory, e.g. "deploy" or "remove" this stack.

Expect, that some parameters (e.g. urls to persisting services) may
point out of the stacks we manage. The tool shall not manage those
external services, but shall accept configuration parameters, pointing
to them.

Out of scope:

-  creation of swarm nodes - they are assumed to exist
-  creation of docker images - this is task of developers, CI/CD etc.

Requirements
------------

The tool shall:

-  help managing configuration of one or more docker swarm stacks
-  support reuse of:

   -  service configuration blocks in ``docker-compose.yml``
   -  single configuration parameter across of multiple services or
      stacks

-  allow seasy update procedure of docker swarm secrets and configs
-  identify all really configurable parameters and allow easy
   modification of any or all of them
-  keep it simple:

   -  focus on managing configurations
   -  do not try to replace docker swarm tooling
   -  assume docker swarm cluster is already available, leave managing
      nodes to other tools

-  support modified deployment of the same stack into different
   environments
-  allow creation of stack configuration library (StaCoLib) and their
   easy installation, update and reuse

User Stories
------------

Following user stories shall be supported:

-  As a SysAdmin, I want to deploy single stack
-  As a SysAdmin, I want to deploy multiple stacks
-  As a SysAdmin, I want to update swarm configuration or secret file
-  As a SysAdmin, I want to update docker image(s) used in deployed
   stack
-  As a developer, I want to rewrite existing stack configuration (based
   on ``docker-compose.yml``) into StaCoLib (stack configuration
   library)

Overview - terms, platform, tools
=================================

Terms
-----

- stack: docker swarm stack
- StaCoLib: stack configuration library
- environment:
- (docker swarm) secret:
- (docker swarm) config:
- (docker) context:
- MuStack: Multi Stack
- MuStack source: ``main.jsonnet``
- MuStack object: JSON object, resulting from evaluating ``main.jsonnet``
- MuStack tree: directory tree with ``docker-compose.yml`` files (incl. all files refrenced from it, e.g. configs and secrets) created according to MuStack object. If not specified, it is considered in fixed state (see below)
- pure (MuStack) tree: MuStackStree, where all references to internal secrets and configs in ``docker-compose.yml`` are in it's original form. This is likely to conflict with secrets and configs existing in respective docker swarm cluster.
- fixed (MuStack) tree: MuStackStree, where all references to internal secrets and configs in ``docker-compose.yml`` got name modified using md5 hash of respective config file content. This shall prevent conflicts with secrets and configs existing in respective docker swarm cluster.

Platform and tools
------------------

Sanky builds on:

-  `Jsonnet <https://jsonnet.org/>`__ - A data templating language for
   app and tool developers. A simple extension of JSON.
-  `Tanka <https://tanka.dev/>`__ - Flexible, reusable and concise
   configuration for Kubernetes
-  `jsonnet
   bundler <https://github.com/jsonnet-bundler/jsonnet-bundler>`__ - A
   jsonnet package manager
-  `Docker Swarm <https://docs.docker.com/engine/swarm/>`__ - native
   clustering functionality for Docker containers
-  `docker-compose <https://docs.docker.com/compose/>`__ - tool for
   defining and running multi-container Docker applications.

Concepts
========

Try to follow scope of tanka - focus on generating parametrized
deployment files and help a bit with deploying it.

What to deploy and where
------------------------

Execution environment: docker swarm cluster
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sanky manage deployment into existing docker swarm cluster.

Deploying multiple stacks
~~~~~~~~~~~~~~~~~~~~~~~~~

Sanky deploys one to N stacks. Think of set of ``docker-compose.yml``
files, each within directory representing stack name they are supposed
to be deployed to.

In fact, user never creates these files directly, sanky generates them
automatically from ``main.json``, which is much better structured as it
defines all parameters across all the stacks being deployed.

(as tanka) multiple deployment environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tanka allows definition of multiple deployment environments, each
separated into special directory with ``main.jsonnet`` file.

Sanky reuses exactly the same tree structure (we shall modify content
and use of ``spec.json`` which refers to exact identification of target
execution environment - sometime called execution context.)

Platform
--------

(as tanka) jsonnet as templating language
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use Jsonnet ability to convert complex set of parameters into whatever
JSON document.

As a result, MuStack object (JSON) defines complete content of MuStack
tree (directory structure and content of all files) ready to be deployed
to docker swarm.

python, golang, jsonnet tools, docker, docker-compose
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tanka is written in golang.

It would be great to have sanky in golang too, but it shall be simpler
(for me) to start with Python.

This will (sometime temporarily) require following tools to be
installed:

-  tanka: (tk) until it is completely rewritten into python (this shall
   be feasible later on)
-  jsonnet: probably handy as CLI for configuration development, but
   python shall manage jsonnet stuff on it's own when needed
-  jsonnet-bundler: (jb) used to install jsonnet libraries. Not planning
   to replace that.
-  docker: this will be always required
-  docker-compose: this will be always required as long as we need to
   use ``docker-compose config``

Prerequisites and workflow
--------------------------

(as tanka) consider docker images for granted
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Do not bother with building docker images, this task is to be fulfilled
by someone else, our task is to assemble things togather and deploy to
target execution environment.

(as tanka) defaults -> modifications -> platform deployment artefacts -> deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tanka supports following process from default application configuration
to customized applicaiton deployment:

-  in ``main.jsonnet`` within given environment directory refer to one
   or more libraries, each defining one application (stack) with default
   configuration
-  in ``main.jsonnet`` allow modification of any library defined
   configuration parameter
-  use transformation process (e.g. ``tk eval .``) to convert
   ``main.jsonnet`` into platform deployment artefacts, usable in target
   execution environment

   -  tanka is targeting Kubernetes, so using set of yaml configuration
      files to send to Kuberenetes
   -  sanky is targeting docker swarm, so using set of
      ``docker-compose.yml`` (and some supporting) files to be applied
      to docker swarm by means of ``docker stack deploy``

-  finally apply platform deployment artefacts int target execution
   environment

Use (python?) tool converting MuStack object into MuStack tree
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Take MuStack object as provided by ``jsonnet`` (or better by
``tk eval .``), but do not attempt to let ``jsonnet`` to create
resulting files (as it has limited capabilities), but better use our
python code to create target MuStack directory tree and files there.

autogenerated swarm secret/config names using content hashes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Docker swarm allows use of secrets/configs. However, once deployed
secret/config cannot be modified, one can only add new one with
different name, which is not used yet.

Usually, this allows to manually maintain secret/config name, e.g. using
sequence numbers, datetime etc.

In our case, the tool automatically assignes secret/config name by
adding hash suffix (md5) based on content of actual file. This ensures,
that the same file gets always exactly the same name without need to
track previous names.

Note, that these names are limited to 64 characters and the md5 hash has
32 characters. In case the configuration provided name is too long, this
configuration provided name is truncated so that the hash is always
present in it's entire length.

(as tanka) generated platform deployment artefacts is not supposed to be edited
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

User is not supposed to manually edit generated platform deployment
artefact.

Tanka allows exporting these artefacts, but this is just for convenience
for reviewing it, real deployment happens without saving these artefacts
to disk.

Sanky (currently) writes these artefacts to disk before deployment but
we shall prevent modifying them manually.

Library as Parametrized application configuration artefact (PACA)
-----------------------------------------------------------------

(as tanka) libsonnet in ``lib`` as parametrized application configuration artefact (PACA)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Each stack shall get jsonnet library, which represents parametrized
model of how given stack can be deployed into target execution
environment.

(as tanka) allow combining multiple PACA into one deployment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Single environment shall allow (within ``main.jsonnet``) combination of
multiple PACA (libraries).

Structuring library and configurations
--------------------------------------

(as tanka) forget about using ``.env`` files for ``docker-compose.yml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``docker-compose.yml`` files, generated by using particular libraries,
may not use any sort of environment variable files or even external
environment variables. This would break rule of "hermetic builds".
Instead, move all environmental parameters into ``./config.libsonnet``
file and in ``lib.libsonnet`` render those values into explicit
environment variable values within ``docker-compose.yml`` file.

(as tanka) library shall separate configuration parameters from templating
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: this is design pattern to follow, not a requirement

Library shall consist of following parts:

-  ``lib.libsonnet``: entry point dealing with templating. It imports
   ``./config.libsonnet``
-  ``./config.libsonnet``: extracted application configuration
   parameters. User can find here all parameters, which can be
   overridden in real deployment.
-  ``./func.libsonnet``: (if needed) functions to call when templating.

(as tanka) separate config for image names and other config parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``./config.libsonnet`` shall have separate (private) key ``_images`` for
specificaiton of docker images to use, and another key ``_config`` for
remaining parameters.

(as tanka) each application using it's configuration namespace
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: this is not always used in tanka, but must be used with sanky.

With tanka, each ``_config`` and ``_images`` key may have separate
subkey called namespace. This might refer to Kubernetes concept of
namespaces (but this I am not sure about).

With sanky, this namespace is obligatory and refers to deployment stack
name (as each applicaiton is expected to run in it's own stack).

This allows keeping configuration of different applications independent.

Intended subcommands
--------------------

TODO

Specifications
==============

MuStack source
--------------

MuStack source is ``main.jsonnet`` file, located in environment as
created by tanka tool.

When calling ``tk eval .`` in given directory, it must evaluate int
MuStack object as defined below.

MuStack object
--------------

MuStack object is JSON document defining directory tree for swarm
stacks.

It has three levels:

-  property: stack name
-  property: target file name
-  value: target file content

If it would be converted to YAML format (for readibility in this
document), it could look like:

.. code:: yaml

   stack_alpha:
     "docker-compose.yml": |
       version: '3.7'
       services:
         web:
           image: stackdemo:v1234
           ports:
             - "8000:8000"
   stack_beta:
     "docker-compose.yml": |
       version: '3'
       services:
         redis:
           image: redis:alpine
     "secrets/pswd.ini": |
       [default]
       anne = ****
       bert = ****

MuStack object is object (dictionary), having on one key per defined
stack. At least one stack must be present. The example shows stacks
``stack_alpha`` and ``stack_beta``.

Each stack object has one key per target file. The example shows target
file ``docker-compose.yml`` for stack ``stack_alpha`` and target files
``docker-compose.yml`` and ``secrets/pswd.ini`` for ``stack_beta``.

Name of a target file may include zero to n subdirectories using forward
slash delimiter. The target file name must start with directory or file
name, it must not start with ``/`` or "." character.

Value of target file property is text, which is supposed to be written
to disk using UTF-8 encoding.

There must exist at least target file name ``docker-compose.yml`` per
stack.

It is expected, that all files referenced by ``docker-compose.yml`` are
having it's own target file name key present, but tooling does not
attempt to check this completeness.

MuStack tree
------------

MuStack tree is tree of directories with stack configuration files. The
tree is created based on content of MuStack object.

By convention, MuStack tree is written into ``_deploy`` subdirectory of
current environment.

Sample MuStack object above would result in following MuStack tree:

.. code:: shell

   $ ls
   _deploy main.jsonnet spec.json
   $ cd _deploy
   $ tree .
   .
   ├── stack_alpha
   │   └── docker-compose.yml
   └── stack_beta
       ├── docker-compose.yml
       └── secrets
           └── pswd.ini

Open Issues:
============

Specify context for deploying the MuStack.
------------------------------------------

-  possibly using ``spec.json``
-  clarify, how to relate to contexts defined in local docker
   installation.

Tool name: sanky, sáňky, sanka or something else
------------------------------------------------

Refine terms used
-----------------

The text contains couple of special terms, not used so far. It would be
probably worth reviewing these to simplify terms used and ease
understanding.

Are we able to prevent use of env variable during ``docker stack deploy``?
--------------------------------------------------------------------------

Some of our ``docker-compose.yml`` files are using secition
``environment``. We are defining there explicit values, but we shall
make sure, no external environ variable modifies it's value there.

According to doc `Environment variables in
Compose <https://docs.docker.com/compose/environment-variables/>`__ it
seems, that if we assing env variable in ``docker-compose.yml``
explicitly, it is not overriden by external variables.
