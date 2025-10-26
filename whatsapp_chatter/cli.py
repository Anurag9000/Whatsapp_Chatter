from __future__ import annotations

import argparse
import sys
import time
import logging

from .contexts import load_context, ensure_context_file
from .llm import build_system_prompt, build_user_prompt, ollama_generate
from .whatsapp import build_driver, open_whatsapp, select_contact, read_recent_messages, send_message


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="WhatsApp Chatter CLI")
    parser.add_argument("person", help="Contact name as visible in WhatsApp")
    parser.add_argument("--me", dest="my_name", help="Your name for the model context", required=False)
    parser.add_argument(
        "--context",
        help="Context file name under contexts/. Defaults to <person>.txt",
        default=None,
    )
    parser.add_argument("--headless", action="store_true", help="Run browser headless")
    parser.add_argument(
        "--user-data-dir",
        help="Chrome user data dir for persistent login (recommended)",
        default=None,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not send messages; only print the generated reply",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=6.0,
        help="Polling interval in seconds for continuous mode",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Send only one reply and exit (overrides continuous mode)",
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Type the generated message into the composer but do not send",
    )
    parser.add_argument(
        "--initiate",
        action="store_true",
        help="Initiate conversation proactively using context and full history",
    )
    parser.add_argument(
        "--prompt",
        help="Custom focused instruction to steer the model for this run",
        default=None,
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    log = logging.getLogger("whatsapp_chatter")

    person = args.person
    ensure_context_file(person, args.context)
    context_text = load_context(person, args.context)

    log.info("Launching browser (headless=%s, user_data_dir=%s)", args.headless, args.user_data_dir)
    driver = build_driver(headless=args.headless, user_data_dir=args.user_data_dir)
    try:
        log.info("Opening WhatsApp Web and waiting for UI...")
        open_whatsapp(driver)
        log.info("Selecting contact: %s", person)
        select_contact(driver, person)
        log.info("Building system prompt (me=%s, context=%s)", args.my_name, (args.context or f"{person}.txt"))
        system_prompt = build_system_prompt(person, context_text, my_name=args.my_name)

        if args.initiate:
            from .whatsapp import read_all_messages
            log.info("Initiator mode: composing opening message...")
            convo = read_all_messages(driver)
            note = "(Initiate conversation naturally.)"
            if args.prompt:
                note += f" Focus: {args.prompt}"
            user_prompt = build_user_prompt(convo + [note])
            log.info("Calling Ollama to generate opener...")
            reply = ollama_generate(system_prompt, user_prompt)
            print("--- Generated opener ---")
            print(reply)
            if args.preview:
                log.info("Preview mode: typing opener without sending.")
                from .whatsapp import send_message
                # Send without ENTER by modifying send function path: reuse and skip send here
                from selenium.webdriver.common.keys import Keys
                from .whatsapp import _find_composer  # type: ignore
                box = _find_composer(driver)
                box.click(); box.send_keys(reply)
            elif not args.dry_run:
                log.info("Sending opener...")
                from .whatsapp import send_message as do_send
                do_send(driver, reply)
                print("Opener sent.")
            else:
                log.info("Dry-run: opener not sent.")
            if args.once:
                return 0

        if args.once:
            from .whatsapp import read_all_messages
            log.info("Reading full conversation (single-shot mode)...")
            convo = read_all_messages(driver)
            if args.prompt:
                convo = convo + [f"Focus: {args.prompt}"]
            user_prompt = build_user_prompt(convo)
            log.info("Calling Ollama to generate reply...")
            reply = ollama_generate(system_prompt, user_prompt)
            if args.preview:
                log.info("Preview mode: typing reply without sending.")
                from .whatsapp import _find_composer  # type: ignore
                box = _find_composer(driver)
                box.click(); box.send_keys(reply)
                print("--- Typed reply (preview) ---")
                print(reply)
            elif args.dry_run or True:
                # Per user request, default behavior is dry run; print reply
                log.info("Dry-run: showing generated reply only (not sending).")
                print("--- Generated reply (dry-run) ---")
                print(reply)
            else:
                log.info("Sending reply...")
                from .whatsapp import send_message as do_send
                do_send(driver, reply)
                print("Reply sent.")
            return 0

        print("Continuous mode: Ctrl+C to stop. Polling for new incoming messages...")
        from .whatsapp import read_last_message, read_all_messages
        last_seen_text = None

        while True:
            try:
                last = read_last_message(driver)
                if last is None:
                    time.sleep(args.interval)
                    continue
                direction, text = last
                if direction == 'in' and text != last_seen_text:
                    # New incoming message detected
                    log.info("New incoming message detected. Building prompt from full conversation...")
                    convo = read_all_messages(driver)
                    if args.prompt:
                        convo = convo + [f"Focus: {args.prompt}"]
                    user_prompt = build_user_prompt(convo)
                    log.info("Calling Ollama to generate reply...")
                    reply = ollama_generate(system_prompt, user_prompt)
                    if args.preview:
                        log.info("Preview mode: typing reply without sending.")
                        from .whatsapp import _find_composer  # type: ignore
                        box = _find_composer(driver)
                        box.click(); box.send_keys(reply)
                        print("--- Typed reply (preview) ---")
                        print(reply)
                    else:
                        print("--- Generated reply (dry-run) ---")
                        print(reply)
                        # Respect dry-run by default
                        if not args.dry_run:
                            log.info("Sending reply...")
                            from .whatsapp import send_message as do_send
                            do_send(driver, reply)
                            print("Reply sent.")
                    last_seen_text = text
                time.sleep(args.interval)
            except KeyboardInterrupt:
                print("Exiting continuous mode.")
                break
            except Exception as e:
                log.exception("Error in loop: %s", e)
                time.sleep(max(2.0, args.interval))
    finally:
        if args.headless:
            log.info("Closing headless browser.")
            driver.quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
