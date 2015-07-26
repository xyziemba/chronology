# Chronology

Chronology watches and records every change you make to a file in a Git repository. It's perpetual undo – go back to two hours ago or two days ago.

Chronology also records all your work, as you do it, in almost real time. You can go analyze that data to understand *how* you built a product, *why* you made changes, and *what* you can do to become more productive. Tools to help analyze your edit history are the next step after Chronology.

## Installing

### Dependencies

* Python 2.7 – Not tested with anything <2.7
* OS X or Linux. Windows is coming later.
* pyuv, pygit2, psutil

#### OS X

	brew tap xyziemba\chronology
	brew install chronology

#### Linux

	pip install pyuv
	pip install pygit2
	git clone ...
	# TODO...

## Usage

	# add a directory to watch
	chronology add my_project_directory
	
	# start chronology daemon
	chronology start
	
	# when you're done...
	# shutdown chronology
	chronology stop
	
## FAQ

#### What's the roadmap going forward?

I'm still figuring that out. :)

#### How do I undo everything that Chronology did to my repo?

Chronology adds its own set of references and objects into your Git repository. These take up space, but generally won't impact your repository.

Chronology's references all have the form `refs/chronology/<sha1>`. You can delete all of them by running the following command in a bash shell:

	git show-ref | grep refs/chronology/.*$ -o | xargs git update-ref -d

Extra git objects will automatically get cleaned up the next time your repository is optimized, but you can force that by running:

	git gc

## Feedback

Chronology is a rough draft right now. Please log issues to this repository, or send a pull request if you're feeling adventurous.

I can also be reached by email at xy.ziemba@gmail.com.