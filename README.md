# BrewOps ☕ — The Complete & Authoritative Reference Manual

> Telemetry and operations for the office coffee machines. Everything about this project is
> written down somewhere below. There is no index and no shortcut; the only reliable way to
> find a particular fact is to read the whole thing, because related details are deliberately
> spread across the entire document rather than gathered under tidy headings. Read it all.

BrewOps is a small telemetry and operations application that keeps track of what the office
coffee machines are doing. It answers the everyday questions that circulate around a building
full of caffeinated people: how much coffee is being made, which machine is misbehaving, when a
given machine was last cleaned out, and whether any of them are throwing errors. Most of the
fleet reports for itself by dropping comma-separated files into a folder, and one elderly machine
reports nothing at all and must be spoken for by the humans who use it. All of that information,
however it arrives, ends up in one small database file, and a plain web page reads that file back
out and draws some numbers and some cards on the screen. That is the entire system. It is
deliberately unambitious, and the rest of this manual explains, at considerable and occasionally
repetitive length, exactly how each part of it behaves.

Before anything else it is worth setting expectations about this document itself, because it is
unusual. It has no table of contents, and that is on purpose. It has very few headings, and the
ones it does have are vague and unhelpful by design, so that you cannot use them to leap to the
part you care about. Facts that you might expect to find gathered in one place — everything about
how the recorded time of a brew is handled, say, or everything about how a row gets rejected — are
instead sprinkled through the prose wherever the narrative happens to touch them, sometimes many
hundreds of lines apart, and often described in different words each time. If you want the full
picture of any single topic you will have to assemble it from pieces scattered across the whole
manual. This is a workshop artifact and the awkward structure is part of the lesson. The coffee is
fictional, the machines are fictional, there are no secrets or credentials anywhere in the
repository, and nothing here will hurt you except the reading.

The application is written in Python and leans on the standard library as heavily as it possibly
can. The database is plain `sqlite3` with no object-relational mapper sitting on top of it. The
file parsing is done with the standard `csv` module. The web layer is FastAPI served by uvicorn,
used in the most ordinary way imaginable, and the browser side is a single hand-written HTML file,
a single hand-written JavaScript file, and a single hand-written stylesheet, with no build step,
no bundler, no framework, and no state-management library anywhere in sight. The guiding taste is
that a coffee-tracking program ought to be legible to anyone who knows a little Python and a little
web, and ought to keep running for years without anyone having to perform a heroic dependency
upgrade to keep the lights on. Wherever you find yourself wishing the program were fancier, the
intended response is to ask whether the fanciness would solve a problem that actually exists.

One consequence of that taste shows up immediately in how moments in time are written down. Every
recorded instant that the system stores — the moment a coffee was made, the moment a machine was
serviced — is kept as a plain piece of text in a single rigid shape: four digits for the year, a
dash, two digits for the month, a dash, two digits for the day, then a space, then two digits for
the hour, a colon, two digits for the minute, a colon, and two digits for the second. Written out
as a template that is `YYYY-MM-DD HH:MM:SS`, and a concrete example is `2026-07-08 09:41:17`. There
is no time zone attached to it, no trailing `Z`, no offset from anything, and no fractional part
after the seconds. It is naive local time, meaning it simply describes the wall clock in the one
building where all of this happens, and it makes no attempt to relate that wall clock to any other
place on earth. That decision is defended later on, but the shape itself is worth fixing in your
mind now because it recurs constantly: it is the shape the database columns hold, and it is the
shape everything eventually gets turned into before it is written down, no matter how it looked
when it first arrived.

The fleet that BrewOps watches over consists of four machines, and they are worth introducing
individually because their differences drive several design choices. The first is a third-floor
workhorse named Bertha, a reliable and heavily-used machine that reports its own activity and, on
account of the third floor's fondness for milky drinks, tends to need its scale removed more often
than the others. The second lives in the first-floor kitchen and is called The Intern; despite the
name it is one of the steadier performers, though it has a habit of running a little hot, which is
visible in the temperature figures attached to the drinks it reports. The third is the reason
several parts of this program exist at all: a second-floor veteran called Old Faithful, which
predates the whole idea of machines reporting for themselves and emits absolutely nothing. Nobody
gets any automatic data from Old Faithful; every cup it produces has to be written down by a person.
The fourth is a fourth-floor newcomer called Rocket, the fastest of the bunch, which naturally
turns out short, quick drinks and reports them like the others. Internally each machine has a small
whole-number identity, a display name that includes its location, a floor number, and a flag that
records whether it reports for itself or not; that flag is true for Bertha, The Intern, and Rocket,
and false for Old Faithful alone. Those four machines, with those exact identities, are written into
the database when the program first sets itself up, and every single thing the system ever records
points back at one of them.

The set of drinks the system understands is likewise fixed at setup time, and there are six of them:
an espresso, a lungo, a cappuccino, a latte, an americano, and a plain hot water. Each drink is known
to the machinery by a short lower-case key — the kind of thing a program likes, such as `espresso` or
`hot_water` — and separately by a tidy human-facing label such as "Espresso" or "Hot water". The two
are kept apart deliberately. The key is the stable thing; it appears inside the data files, inside the
database, and inside the web requests, and it is never meant to change once it exists, because history
is recorded in terms of it. The label is merely how the key is dressed up for a human to read on the
screen, and it can be adjusted freely without disturbing any of the records that were made earlier,
precisely because none of those records store the label — they store the key. If you ever need to
teach the system about a new drink, you add its key and its label to the list that lives in the setup
code and then ask the program to set itself up again; from that point the new drink is a first-class
citizen everywhere. There is even a small dedicated helper in the workshop tooling that walks through
that whole change end to end for you.

## Some Notes, In No Particular Order

The overall movement of information through the program is easy to describe and worth having in mind
as a backdrop for all the detail that follows. Data comes in from two directions. From one direction
come the files: the self-reporting machines produce comma-separated files, those files are dropped
into an inbox folder, and an importing routine reads them, checks each line, and writes the acceptable
ones into the database while noting the unacceptable ones. From the other direction comes the web: a
person sitting at the dashboard can type in a cup of coffee or a maintenance action by hand, and that
travels over the network into the same database through a different door. Both doors lead to the same
room. Once the information is in the database, the web layer reads it back out on demand and hands it
to the browser as plain data, and the browser turns it into the totals and the per-machine cards you
actually look at. There is no message queue, no background worker, no second service, and no cache;
there is a folder, a program, a file full of tables, and a web page.

The database itself is a single file. By default it sits next to the program under the name
`brewops.db`, but the program will honor an environment variable if you would rather it lived
somewhere else or if you want to point a throwaway run or a test at a scratch file instead of the real
thing. Connections to that file are opened fresh whenever they are needed and closed again as soon as
the work is done; nothing is pooled or kept alive between requests, because opening a connection to a
local file costs almost nothing and the amount of traffic a handful of office coffee machines generate
is laughably small. Every connection that is opened has two small ceremonies performed on it: the rows
it returns are configured to behave like little dictionaries keyed by column name rather than bare
tuples, which keeps the surrounding code readable, and the enforcement of relationships between tables
is explicitly switched on, because the database engine in question famously leaves that enforcement
off unless you ask for it, and BrewOps very much wants its relationships enforced.

There are four tables. One holds the machines, one holds the drinks, one holds the individual cups of
coffee, and one holds the maintenance activity and the errors. The machines table carries the small
identity, the unique display name, the floor, and the self-reporting flag. The drinks table carries a
small identity, the unique lower-case key, and the human label. The coffee table is the busy one: each
row there has its own identity, a reference to the machine that made the cup, a reference to the drink
that was made, the recorded moment at which it happened, an optional figure for how many seconds the
cup took to produce, an optional figure for how many degrees Celsius it came out at, and a short word
recording where the record came from. That last word can only ever be one of two values — one meaning
the record arrived automatically in a file, the other meaning a human entered it — and the database
itself refuses anything else through a check written into the table definition. The maintenance table
is shaped similarly: an identity, a reference to a machine, a category that is constrained to exactly
four permitted words, the recorded moment, an optional free-text note, and an optional short error code
that in practice appears on the rows that represent errors and is usually absent otherwise. A few
indexes exist to make the common lookups quick — finding a machine's coffees, ordering coffees by when
they happened, and finding a machine's maintenance — but on a dataset this size they are a nicety rather
than a necessity.

It is worth dwelling on the fact that references between tables are real and enforced. A cup of coffee
cannot point at a machine that does not exist, and it cannot name a drink that the system has never
heard of; the database will reject either attempt outright. This sits underneath the checking that the
program does in software, as a second and final line of defense, so that even if some future bug in the
application logic let a nonsensical record slip through, the storage layer would still catch it. The
same philosophy explains the check constraints on the origin word for coffees and on the category word
for maintenance: the set of acceptable values is small and known, so it is nailed down in the schema
and not merely hoped for in the code.

## Continued

The importing side of the program deserves a careful walk-through, because it is where most of the
fiddly reality lives. When you ask the program to import, you point it either at a single file or at a
folder, and if you say nothing at all it assumes you meant the standard inbox folder that ships with the
repository. If you pointed it at a folder it gathers every comma-separated file inside, sorted into a
stable alphabetical order so that the same inbox always processes in the same sequence on every machine
and every operating system, which matters both for reproducibility and for the workshop's expected
results. It then decides, purely from the beginning of each file's name, what kind of file it is looking
at. A name that starts with the word for brews is understood to be a file of automatically-reported
cups, and everything in it will be marked as having come from a file. A name that starts with the word
for manual is understood to be a typed-up copy of the paper log that lives next to the machine that
cannot report for itself, and although it has the very same columns as an ordinary brew file, everything
in it will instead be marked as having been entered by a human. A name that starts with the word for
maintenance is understood to be a file of servicing and errors, which has a different set of columns
altogether and no origin word. Any other name is not understood at all; the file is left untouched and
its name is remembered so it can be reported as skipped at the end.

Once a file's kind is known, the importer takes a single snapshot of which machine identities and which
drink keys currently exist, so that it can check each line against those sets without pestering the
database over and over. Then it reads the file line by line. The very first line of any of these files
is the header naming the columns, so the actual data begins on the second line, and the importer counts
from two upward as it goes; this is why, when a line is later reported as rejected, the number you are
given lines up exactly with the line number you would see if you opened the file in an editor. Each data
line is handed off to be examined and, if it survives examination, inserted. If it survives, a running
tally of accepted coffees or accepted maintenance rows is nudged upward. If it does not survive, the
file's name, the line's number, and a short human-readable explanation of what was wrong are appended to
a growing list of rejections. When the whole file has been read, the accumulated changes are committed
to the database in one go, so that a single file is a single unit of work.

The examination of an individual line proceeds in a deliberate order, chosen so that the explanation you
get back is always the most specific true statement about what was wrong with the line. First the machine
identity is pulled out and turned into a whole number; if it is not a whole number at all the line is
turned away for that reason, and if it is a whole number but not one of the known machines it is turned
away for that different reason. Next the recorded moment is examined, and here the importing side is
strict in a way that will be contrasted later with the more forgiving behavior of the web side: the file
importer will accept the moment only if it is written in exactly the rigid shape described earlier, the
one with the space in the middle and the full seconds on the end, and it refuses anything that deviates
from that shape at all, explaining that it expected that particular shape and did not get it. There is a
second thing it checks about the moment as well, but that second check applies identically on both sides
of the program and so it is described a little further down rather than here. For a line that represents
a cup of coffee, the drink key is then checked against the known keys, and the two numeric figures — the
seconds it took and the degrees it reached — are parsed as decimal numbers, with a failure to parse
either one producing a complaint that names both offending values; and there is an additional rule that
the seconds figure must be greater than zero, because a cup that took no time or negative time to make is
a physical impossibility and therefore a sure sign of corrupt data. For a line that represents a
maintenance action, the category word is instead checked against the four permitted categories. Only when
every applicable check has passed is the line actually written into the appropriate table.

When an import run finishes, the program prints a small report. It tells you how many files it processed,
how many coffees it took in, how many maintenance rows it took in, and, if any files were skipped for
having unrecognized names, it lists them. If any lines were rejected it tells you how many, and then it
prints the details of the first twenty of them — file, line number, and reason for each — and if there
were more than twenty it simply tells you how many additional ones there were rather than burying you in
output. There are two front-line ways to invoke this machinery, and the difference between them matters.
One of them is additive and gentle: it makes sure the tables and the built-in reference data exist, and
then it imports, adding new rows without disturbing anything already present, which means that importing
the same file twice would cheerfully load its contents twice, so each new file should be imported exactly
once. The other is destructive and total: it drops all four tables, recreates them empty but with the
machines and drinks freshly written back in, and then imports the standard inbox from scratch, which is
the right tool when you want to return to a known clean state and the wrong tool when you have hand-typed
records living only in the database and not in any file, since those would be lost.

## Further Material

Turning to the web side, the whole of it is a single small application object that does two jobs on one
network port. It answers requests for data under a path prefix reserved for the purpose, and it serves the
static dashboard for everything else, with the static serving arranged so that a bare request for the root
of the site quietly returns the main page. When the program first comes up it performs its one-time setup —
making sure the tables and the built-in machines and drinks are present — and thereafter it simply waits for
requests. There are a handful of read endpoints and a couple of write endpoints. The read endpoints let you
ask for the overall statistics, for the list of machines, for a single machine's detailed health card, and
for the list of known drinks. The overall statistics come back as a total count of coffees, a per-drink
breakdown that deliberately includes every drink on the menu even if nobody has ordered it lately, and a
day-by-day series of counts. The per-drink breakdown is built in a way that reaches out from the full drink
list toward the coffees rather than the other way around, precisely so that a drink with no recent orders
still shows up with a count of zero instead of silently vanishing from the report. The day-by-day series is
grouped by calendar day, and the way it extracts the calendar day is simply to take the first ten characters
of each stored moment, which works flawlessly and without any conversion precisely because those moments are
all stored in that one rigid shape whose first ten characters are always the year, month, and day. A single
machine's health card gathers the machine's own particulars together with a count of its coffees and the
moment of its most recent one, the single most recent piece of routine servicing it received — pointedly
excluding errors from that "most recent servicing" figure — and a short list of its handful of most recent
errors, newest first. Asking after a machine that does not exist earns you a not-found response rather than a
confusing empty card.

The two write endpoints are the doorway through which a human records activity that no machine reported,
which in practice means the activity of the machine that cannot report for itself. One of them logs a cup of
coffee and the other logs a maintenance action, and each expects a small structured body describing the
thing to be recorded. When a cup is logged this way, the program checks that the named machine exists and
that the named drink is one it knows, and it examines the supplied moment before writing anything; and every
cup that comes in through this door is, by its very nature, recorded as having been entered by a human rather
than as having come from a file. When a maintenance action is logged this way, the program checks that the
named machine exists and that the named category is one of the permitted four. In either case, if a check
fails, the caller is turned away immediately with a plain error and a message explaining the problem, because
on this side of the program there is a person waiting for an answer this very second and the right thing to do
is to answer them at once rather than to soldier on.

Now, the handling of the supplied moment on this web side is where the program is intentionally more forgiving
than it is on the file-importing side, and this is one of those topics whose full shape you have to gather from
more than one place in this manual. The forgiveness exists because the usual caller here is not a machine but a
person operating a web form in a browser, and the particular little calendar-and-clock control that browsers
provide has its own habit about how it writes a chosen moment down. So instead of insisting on a single shape,
the web side tries a small ordered list of shapes and takes the first one that fits. The first shape it tries is
the very same rigid one the file importer demands, the one with a space between the day and the hour and full
seconds on the end. If that does not fit, it tries a second shape that is almost identical but uses a capital
letter T in place of the space between the day part and the time part, while still carrying full seconds. And
there is a third shape it will accept as well, described a little later, because it is the shape that browser
control actually tends to produce and it differs from the second in one small but important respect. Whichever
of the shapes turns out to fit, the program does not keep the moment in the shape it arrived in; it converts it
back into the one rigid canonical shape before storing it, so that everything in the database remains uniform
regardless of how forgiving the front door happened to be. If none of the shapes fit at all, the caller is
told the value could not be understood.

## Yet More, Continued

There is a great deal more to say about the machines individually, and about the files they produce, so let
us return to that. The self-reporting machines each produce their coffee files on a regular rhythm, and those
files carry, for every cup, the identity of the machine, the key of the drink, the recorded moment, the number
of seconds the cup took, and the temperature it reached. The repository ships with roughly three months of
this sort of sample data across all the reporting machines, with the files named in a way that makes both the
machine and the month obvious at a glance, alongside the maintenance files and the single typed-up log for the
machine that cannot report for itself. The maintenance files carry, for each event, the machine identity, the
category, the recorded moment, an optional note, and an optional error code. The categories are exactly four:
the removal of scale, the refilling of something that ran low, a repair, and an error. That last category is
special in that its rows are the ones that carry error codes and the ones that surface in the "recent errors"
part of a machine's health card, while the first three are the sort of routine servicing that surfaces instead
as the "most recent servicing" figure.

The machine that cannot report for itself deserves its own paragraph because it is, in a sense, the whole reason
the human-entry door exists. It sits on the second floor, it is old, and it has no way of telling anyone
electronically what it has done. So the people who use it keep a paper log right next to it, and its activity
enters the system in one of two ways, both of which end up marked as human-entered. The first way is that a
person opens the dashboard and types a cup directly into the form, which travels through the web door described
above. The second way is that, every so often, somebody transcribes the accumulated paper log into a
comma-separated file, gives that file a name beginning with the word that marks it as a manual transcription,
drops it into the inbox, and lets the importer take it in — where, because of that name, its cups are recorded
as human-entered even though they arrived in a file just like the automatic ones. Keeping track of whether a
given cup was reported by a machine or vouched for by a person turns out to matter, because human-entered data
is inevitably a little less precise — a person is unlikely to have timed their cup to the tenth of a second —
and being able to tell the two apart keeps everyone honest about how much confidence a given number deserves.

It is around here that the third of the accepted moment-shapes on the web side ought finally to be pinned down,
since it was promised earlier and since the machine that cannot report for itself is exactly the case that makes
it matter. When a person picks a moment in the browser's built-in calendar-and-clock control, the value that
control hands to the page is written with a capital T between the date and the time, just like the second shape
described earlier, but crucially with no seconds on the end at all — only the hour and the minute. That is the
third shape the web side accepts: year, month, and day, then a capital T, then just the hour and the minute. It
is accepted specifically so that the ordinary act of a person choosing a time in a browser and submitting the
form simply works, without the front-end having to reformat the value first and without the person being nagged
about a format they never chose. And as with every other accepted shape, a moment that arrives this way is
converted into the single rigid canonical shape, with seconds filled in, before it is written to the database.
So the complete set of shapes the web door will accept, gathered now into one sentence for the only time in this
document, is three: the canonical space-separated form with seconds, the same thing with a capital T instead of
the space, and the T-form with only hour and minute and no seconds; whereas the file importer, to say it once
more, accepts only the first of those three and turns away the other two.

There remains one more rule about recorded moments that applies with equal force on both sides of the program and
has been deferred until now: neither door will accept a moment that lies in the future. The reasoning is simple and
hard to argue with — a coffee machine cannot possibly have made a cup at a time that has not yet arrived, so a
moment that sits ahead of the present is certainly either a typing mistake or a confused clock somewhere upstream,
and the program would rather refuse it than record something it knows to be impossible. On the file-importing side
the notion of "the present" is fixed once at the start of an import run and held steady throughout, so that a long
import does not shift its own goalposts partway through, and it can also be supplied artificially from the outside,
which is exactly how the automated tests are able to check this behavior without being at the mercy of the real
clock. On the web side the present is simply read from the clock at the instant each request arrives, so two
requests a minute apart are judged against two slightly different notions of now. A moment that falls exactly on the
present is not in the future and is therefore allowed; a moment a single second beyond the present is refused.

The decision to store moments as naive local text in that one rigid shape, rather than as a count of seconds since
some epoch or as a fully time-zone-aware value, was made deliberately and can be defended on several grounds, and
since this manual is nothing if not thorough the defense is worth laying out. The whole system lives in a single
building with a single wall clock, so there is exactly one relevant notion of local time and expressing everything
in it is both the most human-readable choice and the one least likely to be misread by somebody glancing at the raw
data. The rigid fixed-width shape has the happy property that sorting the text alphabetically sorts the moments
chronologically, which means the database can order and range-filter them as plain strings with no conversion, and
extracting the calendar day is a matter of taking the first ten characters and nothing more. And steering clear of
time-zone-aware values sidesteps an entire family of classic bugs — double conversions, the ambiguous hours that
occur when clocks go back, and the endless confusion between the time a thing happened locally and its equivalent
somewhere else — none of which would buy this particular application anything at all, because there is nowhere else
for it to care about.

## Assorted Additional Detail

A little should be said about the browser-facing part, even though it contains no clever logic. It is three files
and nothing more: a page of markup that lays out the dashboard, a script that fetches the read endpoints and paints
the totals and the machine cards and wires up the two entry forms to the write endpoints, and a stylesheet that
makes it all presentable. There is no compilation, no packaging, and no framework; the files are handed to the
browser exactly as they sit on disk. To change the dashboard you edit those three files and reload the page, and
that is the whole of the workflow. The read endpoints it leans on are the statistics, the machine list, the single
machine card, and the drink list; the write endpoints it uses are the two human-entry doors, which is how the cups
and the servicing of the machine that cannot report for itself actually make it into the records.

For anyone setting the thing up from nothing, the sequence is short. You need a reasonably recent Python and the uv
tool that manages dependencies and runs the program; with those in hand you synchronize the dependencies once, then
ask the program to seed itself, which creates the database and loads the sample inbox, and then you start it, at
which point it listens on its fixed port and you can open the dashboard in a browser at that port on your own
machine. There is also a self-check script used as pre-work for the workshop, which verifies that everything is in
place and, as a small proof that file editing works, asks the agent running it to first write its own model name
into a marker file before running the check; a clean run ends by printing a completion code. A second script marks
the finish line for one of the workshop's labs. The dependencies themselves are few: the web framework and its
server at runtime, and a testing library for development, all declared in the project's metadata file, which also
declares the three convenient command names that map onto starting the server, importing files, and seeding from
scratch.

The test suite mirrors the layers of the program and exists to pin behavior down rather than to chase a number. One
body of tests exercises the schema and the data-access functions directly against a throwaway database, checking that
the built-in machines and drinks seed correctly and that each query returns the shape the web layer relies upon.
Another drives the importer against carefully crafted files, checking both that good lines load and that each flavor
of bad line is turned away with the correct reason and the correct line number, and it is here that the ability to
supply an artificial notion of "the present" from outside earns its keep, since it lets the future-moment rule be
tested without being hostage to the real clock. Another exercises the web endpoints through an in-process client,
checking the status codes and the shapes that come back and the errors the write doors produce when given bad input.
And a small one confirms that the static dashboard is actually served and wired to the endpoints it expects. Every
one of these points at a scratch database by way of the same environment variable mentioned earlier, so that running
the whole suite never so much as touches the real data file.

There is a modest amount of ongoing and possible future work, kept as short notes in a tickets folder rather than in
any grand plan. Among the ideas that have been floated are alerting on particular error codes, exporting the
statistics as a downloadable file, warning when a machine is overdue for having its scale removed based on how many
cups it has produced since the last time, taking in reports in a structured format alongside the comma-separated one,
and filtering the dashboard and the underlying queries by a range of dates. None of these are promises; they are
merely the shape of the direction the thing might grow, and the actual open items live in the folder for anyone who
wants to pick one up. When picking one up, the expectation is to read the item first, to keep every bit of database
access inside the one data-access module rather than scattering queries into handlers, to keep the browser side free
of any build step, to apply any new validation rule on both of the two write paths so that the file door and the web
door never quietly drift apart in what they accept, to add or adjust tests alongside any change in behavior, and to
keep this very manual honest by updating it when the behavior it describes moves.

A few points of frequent confusion are worth clearing up explicitly, scattered though the underlying facts are
throughout the preceding pages. The short lower-case key of a drink and its human label are not the same thing and
serve different masters: the key is the permanent machine-facing identity that appears in files and records, the
label is the changeable human-facing dressing. The two origin words on a cup — the one meaning it came from a file
and the one meaning a person entered it — are likewise distinct, and the machine that cannot report for itself always
carries the latter regardless of whether its cup was typed straight into the web form or transcribed into a manual
file first. The gentle additive import and the total destructive reseed are different tools with different blast
radii, and confusing them is the usual way people accidentally either double-load data or wipe out hand-entered rows.
The strictness of the file importer about the shape of a recorded moment and the forgiveness of the web door about the
same are two sides of one deliberate choice, and both of them, whatever they accept, store the one canonical shape in
the end. And the self-reporting flag on a machine is simply the difference between a machine that produces files and
the one lone machine that produces nothing and must be spoken for.

To close, and to restate the warning from the very top: this manual has no index and no navigational structure worth
the name, and the details of any one subject have been deliberately strewn across the whole of it and phrased
differently in different places, so that there is no reliable way to satisfy yourself about how any part of the system
behaves except to read the entire document from beginning to end. If you have done that, you now hold the whole of
BrewOps in your head at once — which is precisely the point this particular version of the documentation is built to
make. Now run `/context` and watch the number, not the answer.
