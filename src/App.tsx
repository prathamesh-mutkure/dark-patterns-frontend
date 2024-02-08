import { useEffect, useRef, useState, ReactNode } from "react";
import { cn } from "./lib/utils";
import { Icons } from "./components/icons";
import { Button } from "./components/ui/button";

import { Input } from "@/components/ui/input";
import { Label } from "./components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./components/ui/card";

function NavLink(
  props: React.DetailedHTMLProps<
    React.AnchorHTMLAttributes<HTMLAnchorElement>,
    HTMLAnchorElement
  >
) {
  return (
    <a
      {...props}
      target={props.target ?? "_blank"}
      rel="noreferrer"
      className={cn("", props.className)}
    >
      <Button variant="ghost">{props.children}</Button>
    </a>
  );
}

function SocialLink({ href, children }: { href: string; children: ReactNode }) {
  return (
    <a
      className="rounded-2xl bg-black hover:bg-white/20 text-white border border-[#4C4C4C] px-4 py-1.5 text-sm font-medium z-20 flex flex-row gap-2 items-center"
      href={href}
      target="_blank"
      rel="noreferer"
    >
      {children}
    </a>
  );
}

function App() {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const urlRef = useRef<HTMLInputElement>(null);

  const [color, setcolor] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<{
    url: string;
    result: string;
  }>({
    url: "",
    result: "",
  });

  function changeNavBg() {
    window.scrollY >= 90 ? setcolor(true) : setcolor(false);
  }

  useEffect(() => {
    window.addEventListener("scroll", changeNavBg);

    return () => {
      window.removeEventListener("scroll", changeNavBg);
    };
  }, []);

  async function onSubmit() {
    const val = urlRef.current?.value;

    if (!val || isLoading) return;

    try {
      setIsLoading(true);

      setResult({
        url: val,
        result: "Loading...",
      });

      // TODO: Backend call here

      setResult({
        url: val,
        result: "The result will show here",
      });
    } catch (error) {
      setResult({
        url: val,
        result: "Error analysing...",
      });

      console.log(error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="relative bg-black text-white" data-theme="light">
      <div className="h-screen w-screen flex flex-col items-center justify-center">
        <header className="w-full fixed top-0 left-0 right-0 z-20">
          <nav
            className={cn(
              "flex gap-6 md:gap-10 lg:gap-16 px-4 py-4 md:px-8 lg:px-12",
              color && "bg-white/15"
            )}
          >
            <a className="flex flex-row items-center gap-2" href="/">
              <img className="h-10 w-10" src="/vite.svg" />
              E-Com Analyzer
            </a>

            <div className="flex-grow"></div>

            <NavLink href="/" target="_self">
              Home
            </NavLink>

            <NavLink href="/#demo" target="_self">
              Demo <Icons.arrowDown className="h-4 w-4" />
            </NavLink>

            <NavLink href="https://ide.betteridea.dev/">Sites</NavLink>

            <NavLink href="#" target="_self">
              Team
            </NavLink>
          </nav>
        </header>

        <section
          id="hero"
          className="relative flex flex-col text-center flex-auto justify-center items-center gap-16 h-screen w-screen"
        >
          <div className="overlay absolute z-10 top-0 bottom-0 left-0 right-0 h-full w-full bg-black"></div>

          <div className="flex flex-row gap-4">
            <SocialLink href="https://twitter.com/betteridea_dev">
              <Icons.fileIcon className="h-4 w-4" fill="white" color="white" />
              Presentation
            </SocialLink>

            <SocialLink href="https://twitter.com/betteridea_dev">
              <Icons.github className="h-4 w-4" />
              GitHub
            </SocialLink>
          </div>

          <h1 className="text-6xl capitalize z-20">
            Dark Patterns Hackathon
            <br />
            Team{" "}
            <span className="bg-gradient-to-r from-blue-400 to-red-400 bg-clip-text text-transparent">
              Crosshackers
            </span>
          </h1>

          <p className="text-gray-400 text-2xl capitalize z-20">
            An platform to protect users from dark patterns.
          </p>

          <a href="/#demo" className="z-10">
            <Button>
              Explore <Icons.arrowDown className="h-4 w-4" />
            </Button>
          </a>
        </section>
      </div>

      <section
        id="demo"
        className="relative h-screen w-screen flex flex-col justify-center items-center gap-16"
      >
        <div className="overlay absolute z-10 top-0 bottom-0 left-0 right-0 h-full w-full bg-black"></div>

        <div className="grid w-full max-w-md items-center gap-1.5 z-20">
          <Label htmlFor="url">Privacy Policy URL</Label>
          <Input type="url" id="url" placeholder="Enter URL" ref={urlRef} />
        </div>

        <Button type="button" onClick={onSubmit} className="z-20">
          Analyze
        </Button>

        {result.result && (
          <Card className="w-full max-w-md z-20">
            <CardHeader>
              <CardTitle>{result.url}</CardTitle>
              <CardDescription>Here's the analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <p>{result.result}</p>
            </CardContent>
          </Card>
        )}
      </section>
    </main>
  );
}

export default App;
