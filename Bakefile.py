import bakery.recipes.file as File

#--------------------------------------------------------------------
BASE_ROM = 'Super Mario World (U) [!].smc'

#--------------------------------------------------------------------
@recipe('directory', temp='directory')
async def unzip_archive(archive, directory):
    await shell('unzip', archive, '-d', directory)
    return directory

@recipe('directory', temp='directory')
async def unrar_archive(archive, directory):
    await shell('unrar', 'e', archive, directory + '/')
    return directory

@recipe('output_rom')
async def patch_rom(base_rom, patch_file, output_rom):
    await shell('flips', '--apply', patch_file, base_rom, output_rom)
    return output_rom

#--------------------------------------------------------------------
@build
class BatchRomPatch:
    @provide
    def base_rom(self):
        if not File.exists(BASE_ROM):
            raise Exception("Base rom file is missing: %s" % BASE_ROM)
        return BASE_ROM
    
    @provide
    @temp
    def build_dir(self):
        return File.directory('build')

    @provide
    def output_dir(self):
        return File.directory('output')

    @provide
    def zip_archives(self):
        return File.glob('archives/*.zip')

    @provide
    def rar_archives(self):
        return File.glob('archives/*.rar')

    @provide
    def patches(self):
        return (File.glob('patches/*.ips') +
                File.glob('patches/*.bps'))

    @provide
    def expanded_archives(self, build_dir, zip_archives, rar_archives):
        return [*[unzip_archive(ar, File.join(build_dir, 
            File.drop_ext(File.basename(ar))))
                for ar in zip_archives],
                *[unrar_archive(ar, File.join(build_dir,
            File.drop_ext(File.basename(ar))))
                for ar in rar_archives]]

    @provide
    def archive_patch_files(self, build_dir, expanded_archives):
        return (File.glob(File.join(build_dir, '**/*.ips')) +
                File.glob(File.join(build_dir, '**/*.bps')))

    @provide
    def all_patches(self, archive_patch_files, patches):
        return archive_patch_files + patches

    @default
    def patched_roms(self, patches: 'all_patches', base_rom, output_dir):
        return [patch_rom(base_rom, pt, File.join(output_dir, (
            File.drop_ext(File.basename(pt)) +
            File.splitext(base_rom)[1])))
                for pt in patches]

