;;; torth-mode.el --- Major Mode for editing Torth code -*- lexical-binding: t -*-

;; create the list for font-lock.
;; each category of keyword is given a particular face
(setq torth-font-lock-keywords
      (let* (
             ;; define several category of keywords
	         (x-keywords '("assign" "break" "do" "done" "elif" "else" "endif" "if" "include" "while"))
	         (x-types '("any" "bool" "char" "cstr" "fn" "int" "none" "ptr" "str" "Array" "List" "LinkedList"))
             (x-functions '("class" "const" "end" "endclass" "enum" "function" "in" "inline" "method" "peek" "return" "take"))

	         ;; generate regex string for each category of keywords
             (x-keywords-regexp (regexp-opt x-keywords 'words))
             (x-types-regexp (regexp-opt x-types 'words))
             (x-functions-regexp (regexp-opt x-functions 'words)))

        `(
          (,x-types-regexp . 'font-lock-type-face)
          (,x-functions-regexp . 'font-lock-keyword-face)
          (,x-keywords-regexp . 'font-lock-keyword-face)
          )))

;;;###autoload
(define-derived-mode torth-mode c-mode "torth mode"
  "Major mode for editing Torth code"

  ;; code for syntax highlighting
  (setq font-lock-defaults '((torth-font-lock-keywords))))

;;;###autoload
(add-to-list 'auto-mode-alist '("\\.torth\\'" . torth-mode))

;; add the mode to the 'features' list
(provide 'torth-mode)

;; Install dependencies
(rc/require 'highlight-numbers)

;;; mylsl-mode.el ends here
