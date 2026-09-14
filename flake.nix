{
  description = "Mosaic and dot-to-dot artwork tools";
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  outputs = { self, nixpkgs }:
    let
      systems = [ "aarch64-darwin" "x86_64-darwin" "aarch64-linux" "x86_64-linux" ];
    in {
      devShells = nixpkgs.lib.genAttrs systems (system:
        let pkgs = import nixpkgs { inherit system; };
        in {
          default = pkgs.mkShell {
            packages = [ (pkgs.python3.withPackages (ps: [ ps.pillow ps.numpy ps.scipy ps.opencv4 ps.websocket-client ])) ];
          };
        });
    };
}
