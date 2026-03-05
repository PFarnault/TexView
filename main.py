import argparse
from pathlib import Path
import textwrap

EXT_ORDER = ['.tex', '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.eps']

Preamble = r'''
\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{graphicx}
\usepackage{pdfpages}
\usepackage{hyperref}
\usepackage{fancyvrb}
\pagestyle{plain}
\begin{document}
'''.lstrip()

Footer = r'''
\end{document}
'''

def make_master(input_folder: Path, output_file: Path):
    files = sorted(input_folder.iterdir(),
                   key=lambda p: (EXT_ORDER.index(p.suffix.lower()) 
                                  if p.suffix.lower() in EXT_ORDER else len(EXT_ORDER),
                                  p.name.lower()))
    with open(output_file, 'w', encoding='utf8') as f:
        f.write(Preamble)
        for p in files:
            rel = p.relative_to(output_file.parent)
            f.write('\n\\clearpage\n')
            if p.suffix.lower() == '.pdf':
                f.write(f'\\includepdf[pages=-,fitpaper=true]{{{rel.as_posix()}}}\n')
            elif p.suffix.lower() in ['.png','.jpg','.jpeg']:
                f.write(textwrap.dedent(f'''
                    \\begin{{figure}}[!ht]
                      \\centering
                      \\includegraphics[width=\\textwidth]{{{rel.as_posix()}}}
                    \\end{{figure}}
                '''))
            elif p.suffix.lower() == '.tex':
                f.write(f'\\input{{{rel.as_posix()}}}\n')
               
            elif p.suffix == '.txt':
                f.write(textwrap.dedent(f'''
                    \\section*{{{p.stem}}}
                    \\VerbatimInput{{{rel.as_posix()}}}
                '''))
            else:
                # fallback: treat as image
                f.write(textwrap.dedent(f'''
                    \\begin{{figure}}[!ht]
                      \\centering
                      \\includegraphics[width=\\textwidth]{{{rel.as_posix()}}}
                    \\end{{figure}}
                '''))
        f.write(Footer)

def main():
    parser = argparse.ArgumentParser(description="Generate a TeX booklet from a folder of PDFs, images, and .tex files.")
    parser.add_argument('--input-folder', '-i', type=Path, required=True,
                        help="Folder containing PDFs, PNGs, TEXs")
    parser.add_argument('--output', '-o', type=Path, default=Path('main.tex'),
                        help="Path to write the master .tex file")
    args = parser.parse_args()

    if not args.input_folder.is_dir():
        parser.error(f"{args.input_folder} is not a directory")
    make_master(args.input_folder, args.output)
    print(f"Written {args.output}. You can now run:\n  pdflatex {args.output.name}")

if __name__ == '__main__':
    main()
