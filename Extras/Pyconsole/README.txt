
== Shell for Civ4 ==

This extensions expands the Civ4 application by
a local TCP interface. You can send arbitary 
python commands to the running instance.

Setup:

1. Place Civ4ShellBackend.py into [Your mod]\Assets\Python

2. Add the following lines into your CvEventManager.py:

    # At head of file:
    CIV4_SHELL = True
    if CIV4_SHELL:
        import Civ4ShellBackend
        civ4Console = Civ4ShellBackend.Server(tcp_port=3333)

    # In CvEventManager.__init__:
            if CIV4_SHELL:
                self.glob = globals()
                self.loc = locals()
                civ4Console.init()

    # In CvEventManager.onGameUpdate
            if CIV4_SHELL:
                civ4Console.update(self.glob, self.loc)

3. Start Civ4 and load a game.

4. Type
     'python Pyconsole [port]' 
   into a local terminal window.  

5. Run 'test' in the new subshell to
   send a few commands to the Civ4 instance.

