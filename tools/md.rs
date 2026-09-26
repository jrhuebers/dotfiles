use std::env;
use std::fs::{self, File, OpenOptions};
use std::io::{self, IsTerminal, Read, Write};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

// These are the colors from Glamour's built-in LightStyle, which Glow uses.
const NORMAL_FG: u8 = 234;
const HEADING_FG: u8 = 27;
const H1_FG: u8 = 228;
const H1_BG: u8 = 63;
const RULE_FG: u8 = 249;
const LINK_FG: u8 = 36;
const LINK_TEXT_FG: u8 = 29;
const INLINE_CODE_FG: u8 = 203;
const INLINE_CODE_BG: u8 = 254;
const CODE_BLOCK_FG: u8 = 242;

const RESET: &str = "\x1b[0m";
const BOLD: &str = "\x1b[1m";
const ITALIC: &str = "\x1b[3m";
const UNDERLINE: &str = "\x1b[4m";
const DIM: &str = "\x1b[2m";

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.iter().any(|arg| arg == "-h" || arg == "--help") {
        println!("Usage: md [FILE ...]\n\nRender Markdown and read it in a pager. Use - for standard input.\nWhen given a directory, select a Markdown file interactively.");
        return;
    }
    if args.iter().any(|arg| arg == "--version") {
        println!("md 0.2.0");
        return;
    }

    let paths = match choose_paths(&args) {
        Ok(Some(paths)) => paths,
        Ok(None) => return,
        Err(error) => {
            eprintln!("md: {error}");
            std::process::exit(2);
        }
    };
    let input = match read_input(&paths) {
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

fn choose_paths(args: &[String]) -> io::Result<Option<Vec<String>>> {
    if args.len() == 1 {
        let candidate = Path::new(&args[0]);
        if candidate.is_dir() {
            return select_paths(candidate);
        }
    }
    if args.is_empty() && io::stdin().is_terminal() {
        return select_paths(Path::new("."));
    }
    Ok(Some(args.to_vec()))
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
            output.push_str(&fg(CODE_BLOCK_FG));
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
            if level == 1 {
                output.push_str(&style(H1_FG, Some(H1_BG), true, false, false));
                output.push(' ');
                output.push_str(&render_inline(heading.trim(), H1_FG));
                output.push(' ');
            } else {
                output.push_str(&style(HEADING_FG, None, true, false, false));
                output.push_str(&render_inline(heading.trim(), HEADING_FG));
            }
            output.push_str(RESET);
            output.push('\n');
            if level > 1 {
                output.push('\n');
            }
            continue;
        }
        if is_rule(trimmed) {
            flush_paragraph(&mut paragraph, &mut output);
            output.push_str(&fg(RULE_FG));
            output.push_str("────────────────────────────────────────");
            output.push_str(RESET);
            output.push('\n');
            continue;
        }
        if let Some(content) = list_item(trimmed) {
            flush_paragraph(&mut paragraph, &mut output);
            output.push_str(&fg(NORMAL_FG));
            output.push_str(content.0);
            output.push_str(&render_inline(content.1, NORMAL_FG));
            output.push_str(RESET);
            output.push('\n');
            continue;
        }
        if let Some(content) = trimmed.strip_prefix("> ").or_else(|| trimmed.strip_prefix('>')) {
            flush_paragraph(&mut paragraph, &mut output);
            output.push_str(&fg(NORMAL_FG));
            output.push_str(DIM);
            output.push_str("│ ");
            output.push_str(RESET);
            output.push_str(&render_inline(content.trim(), NORMAL_FG));
            output.push_str(RESET);
            output.push('\n');
            continue;
        }
        paragraph.push(line.trim().to_string());
    }

    flush_paragraph(&mut paragraph, &mut output);
    add_margins(&output)
}

fn flush_paragraph(paragraph: &mut Vec<String>, output: &mut String) {
    if paragraph.is_empty() {
        return;
    }
    let joined = paragraph.join(" ");
    output.push_str(&render_inline(&joined, NORMAL_FG));
    output.push_str(RESET);
    output.push('\n');
    paragraph.clear();
}

fn add_margins(rendered: &str) -> String {
    let mut output = String::with_capacity(rendered.len() + rendered.lines().count() * 2);
    for line in rendered.split_inclusive('\n') {
        output.push(' ');
        output.push_str(line.trim_end_matches('\n'));
        output.push(' ');
        output.push('\n');
    }
    output
}

fn fg(color: u8) -> String {
    format!("\x1b[38;5;{color}m")
}

fn style(foreground: u8, background: Option<u8>, bold: bool, italic: bool, underline: bool) -> String {
    let mut result = fg(foreground);
    if let Some(background) = background {
        result.push_str(&format!("\x1b[48;5;{background}m"));
    }
    if bold {
        result.push_str(BOLD);
    }
    if italic {
        result.push_str(ITALIC);
    }
    if underline {
        result.push_str(UNDERLINE);
    }
    result
}

fn restore(foreground: u8) -> String {
    format!("{RESET}{}", fg(foreground))
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

fn render_inline(input: &str, base_foreground: u8) -> String {
    let mut output = String::with_capacity(input.len() + 16);
    output.push_str(&fg(base_foreground));
    let mut index = 0;
    while index < input.len() {
        let rest = &input[index..];
        if rest.starts_with("**") || rest.starts_with("__") {
            let marker = &input[index..index + 2];
            if let Some(end) = input[index + 2..].find(marker) {
                output.push_str(BOLD);
                output.push_str(&render_inline(&input[index + 2..index + 2 + end], base_foreground));
                output.push_str(&restore(base_foreground));
                index += end + 4;
            } else {
                output.push_str(marker);
                index += 2;
            }
            continue;
        }
        if rest.starts_with('`') {
            if let Some(end) = input[index + 1..].find('`') {
                output.push_str(&style(INLINE_CODE_FG, Some(INLINE_CODE_BG), false, false, false));
                output.push(' ');
                output.push_str(&input[index + 1..index + 1 + end]);
                output.push(' ');
                output.push_str(&restore(base_foreground));
                index += end + 2;
                continue;
            }
        }
        if rest.starts_with('[') {
            if let Some(close) = input[index + 1..].find("](") {
                let close = index + 1 + close;
                if let Some(end) = input[close + 2..].find(')') {
                    let end = close + 2 + end;
                    output.push_str(&style(LINK_TEXT_FG, None, true, false, true));
                    output.push_str(&input[index + 1..close]);
                    output.push_str(&style(LINK_FG, None, false, false, true));
                    output.push_str(" <");
                    output.push_str(&input[close + 2..end]);
                    output.push_str(">");
                    output.push_str(&restore(base_foreground));
                    index = end + 1;
                    continue;
                }
            }
        }
        if rest.starts_with('*') || rest.starts_with('_') {
            let marker = &input[index..index + 1];
            if let Some(end) = input[index + 1..].find(marker) {
                output.push_str(ITALIC);
                output.push_str(&input[index + 1..index + 1 + end]);
                output.push_str(&restore(base_foreground));
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

fn select_paths(directory: &Path) -> io::Result<Option<Vec<String>>> {
    let mut files = Vec::new();
    collect_markdown_files(directory, directory, &mut files)?;
    files.sort_by(|left, right| left.to_string_lossy().cmp(&right.to_string_lossy()));
    if files.is_empty() {
        return Err(io::Error::new(io::ErrorKind::NotFound, "no Markdown files found"));
    }

    let mut tty = OpenOptions::new().read(true).write(true).open("/dev/tty")?;
    let saved = stty(&["-g"])?;
    stty(&["-icanon", "-echo", "min", "1", "time", "0"])?;
    let selected = picker_loop(&mut tty, &files)?;
    let _ = restore_tty(&saved);
    print!("\x1b[2J\x1b[H");
    io::stdout().flush()?;

    Ok(selected.map(|path| {
        vec![directory.join(path).to_string_lossy().into_owned()]
    }))
}

fn collect_markdown_files(directory: &Path, root: &Path, files: &mut Vec<PathBuf>) -> io::Result<()> {
    for entry in fs::read_dir(directory)? {
        let entry = entry?;
        let path = entry.path();
        let name = entry.file_name();
        if name.to_string_lossy().starts_with('.') {
            continue;
        }
        if path.is_dir() {
            collect_markdown_files(&path, root, files)?;
        } else if path.is_file() && is_markdown_file(&path) {
            files.push(path.strip_prefix(root).unwrap_or(&path).to_path_buf());
        }
    }
    Ok(())
}

fn is_markdown_file(path: &Path) -> bool {
    matches!(
        path.extension().and_then(|extension| extension.to_str()).map(|extension| extension.to_ascii_lowercase()).as_deref(),
        Some("md") | Some("mdown") | Some("mkdn") | Some("mkd") | Some("markdown")
    )
}

fn picker_loop(tty: &mut File, files: &[PathBuf]) -> io::Result<Option<PathBuf>> {
    let mut selected = 0usize;
    loop {
        draw_picker(files, selected)?;
        let key = read_key(tty)?;
        match key {
            Key::Up => selected = selected.saturating_sub(1),
            Key::Down => selected = (selected + 1).min(files.len() - 1),
            Key::Enter => return Ok(Some(files[selected].clone())),
            Key::Quit => return Ok(None),
            Key::Other => {}
        }
    }
}

#[derive(Clone, Copy)]
enum Key {
    Up,
    Down,
    Enter,
    Quit,
    Other,
}

fn read_key(tty: &mut File) -> io::Result<Key> {
    let mut byte = [0u8; 1];
    tty.read_exact(&mut byte)?;
    match byte[0] {
        b'k' | 0x10 => Ok(Key::Up),
        b'j' | 0x0e => Ok(Key::Down),
        b'\r' | b'\n' => Ok(Key::Enter),
        b'q' | 0x03 | 0x1b => {
            if byte[0] == 0x1b {
                let mut escape = [0u8; 2];
                tty.read_exact(&mut escape)?;
                match escape {
                    [b'[', b'A'] => return Ok(Key::Up),
                    [b'[', b'B'] => return Ok(Key::Down),
                    _ => {}
                }
            }
            Ok(Key::Quit)
        }
        _ => Ok(Key::Other),
    }
}

fn draw_picker(files: &[PathBuf], selected: usize) -> io::Result<()> {
    let rows = terminal_rows().unwrap_or(24) as usize;
    let visible = rows.saturating_sub(5).max(1);
    let first = selected.saturating_sub(visible - 1).min(files.len() - visible.min(files.len()));
    let last = (first + visible).min(files.len());

    let mut screen = String::from("\x1b[2J\x1b[H");
    screen.push(' ');
    screen.push_str(&style(H1_FG, Some(H1_BG), true, false, false));
    screen.push_str(" md ");
    screen.push_str(RESET);
    screen.push_str(" select a Markdown file\n\n");
    for (index, path) in files.iter().enumerate().skip(first).take(last - first) {
        screen.push(' ');
        if index == selected {
            screen.push_str("\x1b[38;2;238;111;248m\x1b[1m❯ ");
        } else {
            screen.push_str("\x1b[38;2;4;181;117m  ");
        }
        screen.push_str(&path.to_string_lossy());
        screen.push_str(RESET);
        screen.push('\n');
    }
    screen.push_str("\n ");
    screen.push_str(DIM);
    screen.push_str("↑/↓ or j/k  enter open  q quit");
    screen.push_str(RESET);
    print!("{screen}");
    io::stdout().flush()
}

fn terminal_rows() -> Option<u16> {
    let output = Command::new("stty").args(["-F", "/dev/tty", "size"]).output().ok()?;
    let text = String::from_utf8_lossy(&output.stdout);
    text.split_whitespace().next()?.parse().ok()
}

fn stty(arguments: &[&str]) -> io::Result<String> {
    let output = Command::new("stty").arg("-F").arg("/dev/tty").args(arguments).output()?;
    if !output.status.success() {
        return Err(io::Error::new(io::ErrorKind::Other, "unable to configure terminal"));
    }
    Ok(String::from_utf8_lossy(&output.stdout).trim().to_string())
}

fn restore_tty(saved: &str) -> io::Result<()> {
    let output = Command::new("stty").args(["-F", "/dev/tty", saved]).output()?;
    if output.status.success() {
        Ok(())
    } else {
        Err(io::Error::new(io::ErrorKind::Other, "unable to restore terminal"))
    }
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
