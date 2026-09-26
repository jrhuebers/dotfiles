use std::env;
use std::fs;
use std::io::{self, Read, Write};
use std::process::{Command, Stdio};

const RESET: &str = "\x1b[0m";
const BOLD: &str = "\x1b[1m";
const UNDERLINE: &str = "\x1b[4m";
const DIM: &str = "\x1b[2m";
const REVERSE: &str = "\x1b[7m";

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.iter().any(|arg| arg == "-h" || arg == "--help") {
        println!("Usage: md [FILE ...]\n\nRender Markdown and read it in a pager. Use - for standard input.");
        return;
    }
    if args.iter().any(|arg| arg == "--version") {
        println!("md 0.1.0");
        return;
    }

    let input = match read_input(&args) {
        Ok(input) => input,
        Err(error) => {
            eprintln!("md: {error}");
            std::process::exit(2);
        }
    };
    let rendered = render_markdown(&input);

    if let Err(error) = page(&rendered) {
        eprintln!("md: {error}");
        std::process::exit(1);
    }
}

fn read_input(paths: &[String]) -> io::Result<String> {
    if paths.is_empty() {
        let mut input = String::new();
        io::stdin().read_to_string(&mut input)?;
        return Ok(input);
    }

    let mut combined = String::new();
    for (index, path) in paths.iter().enumerate() {
        if index > 0 {
            combined.push_str("\n\n");
        }
        if path == "-" {
            io::stdin().read_to_string(&mut combined)?;
        } else {
            combined.push_str(&fs::read_to_string(path)?);
        }
    }
    Ok(combined)
}

fn render_markdown(input: &str) -> String {
    let mut output = String::with_capacity(input.len() + input.len() / 8);
    let mut paragraph: Vec<String> = Vec::new();
    let mut in_code = false;

    for raw_line in input.lines() {
        let line = raw_line.strip_suffix('\r').unwrap_or(raw_line);
        let trimmed = line.trim_start();

        if is_fence(trimmed) {
            flush_paragraph(&mut paragraph, &mut output);
            in_code = !in_code;
            continue;
        }
        if in_code {
            output.push_str("  ");
            output.push_str(DIM);
            output.push_str(REVERSE);
            output.push_str(line);
            output.push_str(RESET);
            output.push('\n');
            continue;
        }
        if line.trim().is_empty() {
            flush_paragraph(&mut paragraph, &mut output);
            if !output.ends_with("\n\n") && !output.is_empty() {
                output.push('\n');
            }
            continue;
        }
        if let Some((level, heading)) = heading(trimmed) {
            flush_paragraph(&mut paragraph, &mut output);
            output.push_str(BOLD);
            output.push_str(UNDERLINE);
            output.push_str(&render_inline(heading.trim()));
            output.push_str(RESET);
            output.push('\n');
            if level > 1 {
                output.push('\n');
            }
            continue;
        }
        if is_rule(trimmed) {
            flush_paragraph(&mut paragraph, &mut output);
            output.push_str(DIM);
            output.push_str("────────────────────────────────────────");
            output.push_str(RESET);
            output.push('\n');
            continue;
        }
        if let Some(content) = list_item(trimmed) {
            flush_paragraph(&mut paragraph, &mut output);
            output.push_str(content.0);
            output.push_str(&render_inline(content.1));
            output.push('\n');
            continue;
        }
        if let Some(content) = trimmed.strip_prefix("> ").or_else(|| trimmed.strip_prefix('>')) {
            flush_paragraph(&mut paragraph, &mut output);
            output.push_str(DIM);
            output.push_str("│ ");
            output.push_str(RESET);
            output.push_str(&render_inline(content.trim()));
            output.push('\n');
            continue;
        }
        paragraph.push(line.trim().to_string());
    }

    if in_code {
        // A missing closing fence is still useful as a code block in a pager.
    }
    flush_paragraph(&mut paragraph, &mut output);
    output
}

fn flush_paragraph(paragraph: &mut Vec<String>, output: &mut String) {
    if paragraph.is_empty() {
        return;
    }
    let joined = paragraph.join(" ");
    output.push_str(&render_inline(&joined));
    output.push('\n');
    paragraph.clear();
}

fn is_fence(line: &str) -> bool {
    line.starts_with("```") || line.starts_with("~~~")
}

fn heading(line: &str) -> Option<(usize, &str)> {
    let level = line.chars().take_while(|character| *character == '#').count();
    if (1..=6).contains(&level) && line.chars().nth(level) == Some(' ') {
        Some((level, &line[level + 1..]))
    } else {
        None
    }
}

fn is_rule(line: &str) -> bool {
    let compact: String = line.chars().filter(|character| !character.is_whitespace()).collect();
    compact.len() >= 3
        && (compact.chars().all(|character| character == '-')
            || compact.chars().all(|character| character == '*')
            || compact.chars().all(|character| character == '_'))
}

fn list_item(line: &str) -> Option<(&str, &str)> {
    if let Some(content) = line.strip_prefix("- ").or_else(|| line.strip_prefix("* ")).or_else(|| line.strip_prefix("+ ")) {
        return Some(("• ", content));
    }
    let dot = line.find(". ")?;
    if dot > 0 && line[..dot].chars().all(|character| character.is_ascii_digit()) {
        return Some((&line[..dot + 2], &line[dot + 2..]));
    }
    None
}

fn render_inline(input: &str) -> String {
    let mut output = String::with_capacity(input.len() + 16);
    let mut index = 0;
    while index < input.len() {
        let rest = &input[index..];
        if rest.starts_with("**") || rest.starts_with("__") {
            let marker = &input[index..index + 2];
            if let Some(end) = input[index + 2..].find(marker) {
                output.push_str(BOLD);
                output.push_str(&input[index + 2..index + 2 + end]);
                output.push_str(RESET);
                index += end + 4;
            } else {
                output.push_str(marker);
                index += 2;
            }
            continue;
        }
        if rest.starts_with('`') {
            if let Some(end) = input[index + 1..].find('`') {
                output.push_str(REVERSE);
                output.push_str(&input[index + 1..index + 1 + end]);
                output.push_str(RESET);
                index += end + 2;
                continue;
            }
        }
        if rest.starts_with('[') {
            if let Some(close) = input[index + 1..].find("](") {
                let close = index + 1 + close;
                if let Some(end) = input[close + 2..].find(')') {
                    let end = close + 2 + end;
                    output.push_str(UNDERLINE);
                    output.push_str(&input[index + 1..close]);
                    output.push_str(RESET);
                    output.push_str(" <");
                    output.push_str(&input[close + 2..end]);
                    output.push('>');
                    index = end + 1;
                    continue;
                }
            }
        }
        if rest.starts_with('*') || rest.starts_with('_') {
            let marker = &input[index..index + 1];
            if let Some(end) = input[index + 1..].find(marker) {
                output.push_str(UNDERLINE);
                output.push_str(&input[index + 1..index + 1 + end]);
                output.push_str(RESET);
                index += end + 2;
            } else {
                output.push_str(marker);
                index += 1;
            }
            continue;
        }
        let character = rest.chars().next().unwrap();
        output.push(character);
        index += character.len_utf8();
    }
    output
}

fn page(rendered: &str) -> io::Result<()> {
    let pager = env::var("PAGER").unwrap_or_else(|_| "less -R".to_string());
    let words = shell_words(&pager).ok_or_else(|| io::Error::new(io::ErrorKind::InvalidInput, "invalid PAGER"))?;
    if words.is_empty() {
        return Err(io::Error::new(io::ErrorKind::InvalidInput, "empty PAGER"));
    }

    let mut child = Command::new(&words[0])
        .args(&words[1..])
        .stdin(Stdio::piped())
        .stdout(Stdio::inherit())
        .stderr(Stdio::inherit())
        .spawn()?;
    if let Some(mut stdin) = child.stdin.take() {
        let _ = stdin.write_all(rendered.as_bytes());
    }
    let status = child.wait()?;
    if status.success() {
        Ok(())
    } else {
        Err(io::Error::new(io::ErrorKind::Other, format!("pager exited with {status}")))
    }
}

fn shell_words(input: &str) -> Option<Vec<String>> {
    let mut words = Vec::new();
    let mut word = String::new();
    let mut quote = None;
    let mut escaped = false;
    for character in input.chars() {
        if escaped {
            word.push(character);
            escaped = false;
        } else if character == '\\' && quote != Some('\'') {
            escaped = true;
        } else if let Some(active) = quote {
            if character == active {
                quote = None;
            } else {
                word.push(character);
            }
        } else if character == '\'' || character == '"' {
            quote = Some(character);
        } else if character.is_whitespace() {
            if !word.is_empty() {
                words.push(std::mem::take(&mut word));
            }
        } else {
            word.push(character);
        }
    }
    if escaped || quote.is_some() {
        return None;
    }
    if !word.is_empty() {
        words.push(word);
    }
    Some(words)
}
